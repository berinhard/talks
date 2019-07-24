# Mocks?
<!-- .slide: class="bg-green-pattern" -->

---

### Descrição de funcionalidade

*No meu sistema de pagamento, preciso processar o pagamento de um cliente para um produto. Isso significa retirar o dinheiro do saldo do cliente e enviar uma mensagem para que ele seja informado. Não podemos processar o pagamento no caso do cliente não ter saldo.*

---

### O que testar no código abaixo?

```python
def processa_pagamento(valor, user, notificador):
    if valor > user.saldo:
        user.saldo -= valor
        notificador.notifica_pagamento(valor, user)
    else:
        raise ValueError("Saldo insuficiente")
```

---

### Cenários de testes

- Se o usuário **não possui saldo**, temos que **levantar a exceção**
- Se o usuário **possui saldo**, temos que **atualizar o saldo** e **notificar** o pagamento
- Como testar a notificação?
- Vamos supor que ela bata num banco de dados lento ou use um serviço de email que demore muito. Como isso impacta nos testes?

---

### Dependências

- O objeto `notificador` **colabora** para que a função desempenhe todo o seu papel isolando a implementação da notificação no método `notifica_pagamento`.
- A função `processa_pagamento` **depende do método** `notifica_pagamento` do objeto `notificador`
- Do ponto de vista desta função, não interessa muito **como** a notificação está implementada, mas sim se ela está sendo chamada corretamente com o `valor` e o `user` corretos
- Do ponto de vista do **test unitário** da função de processamento, podemos garantir isso de jeitos simples através de **`FakeObjects`**.

---

# Fake Objects
<!-- .slide: class="bg-green-pattern" -->

---

###### Working Effectively with Legacy Code

Um *fake object* é um objeto que implementa uma depedência do método ou classe que está sendo **testado unitariamente**. Sua principal utilidade é a de **simplificar as dependências nos testes** para reduzir as suas complexidades.

[Referência](http://xunitpatterns.com/Fake%20Object.html)

---

### Criando um Fake Object

```python
class NotificadorFake:

    def __init__(self):
        self.messages = []

    def notifica_pagamento(self, valor, user):
        msg = f'Pagamento de {valor} por {user}'
        self.messages.append(msg)

    def garante_que_notificou_pagamento(self, valor, user):
        msg = f'Pagamento de {valor} por {user}'
        assert msg in self.messages
```

---

### Testando com Fake Object

```python
def test_processa_pagamento_com_sucesso():
    user = User(saldo=500)
    notificador = NotificadorFake()

    processa_pagamento(100, user, notificador)

    assert user.saldo == 400
    notificador.garante_que_notificou_pagamento(100, user)
```

---

### Problemas com o uso de Fake Object

- A medida que o **número de dependências aumenta** em um objeto, os seus testes precisarão **implementar mais fake objects**
- **Ambivalência constante**: satisfaz tanto o código com a implementação do `notifica_pagamento` quando o teste com o `garante_que_notificou_pagamento`
- #comofaz?

---

# Mocks!
<!-- .slide: class="bg-green-pattern" -->

---

###### Working Effectively with Legacy Code

Um *mock* é um fake object com esteróides. Eles performam asserções internamente validando chamadas de métodos ou invocações de atributos.

[Referência](https://stackoverflow.com/questions/2665812/what-is-mocking#2666006)

---

### Testando com Mock

```python
def test_processa_pagamento_com_sucesso():
    user = User(saldo=500)
    notificador = Mock()   # notificador agora é um objeto Mock

    processa_pagamento(100, user, notificador)

    assert user.saldo == 400
    notificador.notifica_pagamento.assert_called_once_with(100, user)
```

Quais impactos que vocês acham que essa refatoração traz aos testes?

---

### E se a função estivesse com outra implementação...

```python
def processa_pagamento(valor, user):
    notificador = NotificadorEmail()

    if valor > user.saldo:
        user.saldo -= valor
        notificador.notifica_pagamento(valor, user)
    else:
        raise ValueError("Saldo insuficiente")
```

Como fazer para "mockar" o notificador se ele está sendo criado dentro da função?

---

### from unittest import mock
<!-- .slide: class="bg-green-pattern" -->

---

### Mocks Pythônicos

- Era uma lib terceira que foi incorporada ao Python 3.3 via [PEP 417](https://www.python.org/dev/peps/pep-0417/)
- O módulo de mocks do Python nos fornece **diversas maneiras de mockar** classes, objetos e funções
- Elas se diferenciam basicamente **no uso ou não da função `patch`**
- Mas, além disso, essas diferenças nos **evidenciam os impactos e qualidades** nas decisões de implementação, ou seja, **no design do nosso código**
- Design do código não é nada sobre estética ou legibilidade, mas sobre **a organização e relação entre as peças que o compõem**
- O conceito de **code design** possui muitas correlações com a parte de **UX na teoria do design**

---

### Questionando o Design via mocks

- Fake Objects ou Mocks nos **evidenciam as dependências** da unidade de código, ou seja, falam sobre o **acoplamento** da unidade a outras partes
- As dependências podem ajudar ou atrapalhar no design a partir do momento que **elas separam responsabilidades**
- Em geral isso está associado ao **quão rígidas e abstratas** elas são
- Quanto **menos rígido e mais abstrato**, melhor
- Vamos começar do mais simples e ir até o mais complexo

---

# Mocks por Dependências
<!-- .slide: class="bg-green-pattern" -->

---

### Dependência simples de objetos

```python
def monta_url_apos_login(user):
    if user.is_admin:
        return '/admin/'
    else:
        return '/'
```

A função `monta_url_apos_login` depende **somente** do atributo `is_admin`

---

### Dependência simples de objetos

```python
def test_monta_url_apos_login():
    # asserção para usuário admin
    user  = Mock(is_admin=True)
    assert '/admin/' == monta_url_apos_login(user)

    user  = Mock(is_admin=False)
    assert '/' == monta_url_apos_login(user)
```

Por conta disso, podemos testar essa função com um Mock simples que controle a flag `is_admin`.

---

### Dependência de comportamento

O software muda: agora existem outras regras para definir se um usuário deve ser redirectionado para `/admin/`.

Todas essas lógicas foram implementadas em um método chamado `has_admin_access()`. Após a refatoração o código ficou da seguinte forma:

```python
def monta_url_apos_login(user):
    if user.has_admin_access():
        return '/admin/'
    else:
        return '/'
```

Agora precisamos mockar **o comportamento do método** `has_admin_access` para nos retornar `True` ou `False`

---

### Dependência de comportamento

```python
def test_monta_url_apos_login():
    # asserção para usuário admin
    user  = Mock()
    user.has_admin_access.return_value = True     # configuramos o comportamento para True
    assert '/admin/' == monta_url_apos_login(user)

    user  = Mock()
    user.has_admin_access.return_value = False    # configuramos o comportamento para False
    assert '/' == monta_url_apos_login(user)
```

Bem-vindos a porta de entrada das loucuras de mocks!

---

### Problemas da abordagem anterior

- O que acontece caso o método `has_admin_access` seja renomeado para `check_for_admin_access`?
- Ou, o que acontece caso o método `has_admin_access` agora precise obrigadoriamente de um novo parâmetro?
- Mesmo após mudarmos a classe `User`, **os testes continuarão passando** (é sério)

---

### Explícito é melhor do Implícito

```python
def test_monta_url_apos_login():
    # no parâmetro spec, definimos qual classe estamos mockando e com isso
    # todos os seus contratos (atributos, métodos e seus parâmetros) serão
    # verificados e levantarão exceções caso sejam inválidos

    user  = Mock(spec=User)
    user.has_admin_access.return_value = True     # configuramos o comportamento para True
    assert '/admin/' == monta_url_apos_login(user)

    user  = Mock(spec=User)
    user.has_admin_access.return_value = False    # configuramos o comportamento para False
    assert '/' == monta_url_apos_login(user)
```

```python
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
----> 1 user.has_admin_access.return_value = True

/usr/lib/python3.6/unittest/mock.py in __getattr__(self, name)
    580         elif self._mock_methods is not None:
    581             if name not in self._mock_methods or name in _all_magics:
--> 582                 raise AttributeError("Mock object has no attribute %r" % name)
    583         elif _is_magic(name):
    584             raise AttributeError(name)

AttributeError: Mock object has no attribute 'has_admin_access'
```

---

### Explícito é melhor do Implícito 2

```python
def test_monta_url_apos_login():
    user  = Mock(spec=User)
    user.check_admin_access.return_value = True
    assert '/admin/' == monta_url_apos_login(user)

    # vamos também garantir se a chamada do método foi certa
    # ou seja, se os parâmetros estão corretos
    assert user.check_admin_access.assert_called_once_with()

    user  = Mock(spec=User)
    user.check_admin_access.return_value = False
    assert '/' == monta_url_apos_login(user)

    assert user.check_admin_access.assert_called_once_with()
```

---

### Simples, não?

- Nos dois exemplos acima, o uso do mock é **muito simples** e isso é uma evidência positiva!
- Somente definimos o **seu comportamento** e **garantimos as expectativas** verificando as chamadas
- Tanto na dependência do objeto quanto do seu comportamento, nós conseguimos do teste fazer **um recorte do que precisamos** preparar para a função
- Mais tecnicamente, conseguimos **definir a interface pública** da classe `User`
- Além disso, nós conseguimos criar o mock no teste porque estamos **injetando a dependência** através do parâmetro `user`
- Essa injeção é o que deixa a função `monta_url_apos_login` com um **baixo grau de rigidez** e, no caso da dependência do comportamento, **alto de abstração**

---

# Mocks de Referências
<!-- .slide: class="bg-green-pattern" -->

---

### Voltando a onde paramos no nosso exemplo...

```python
def processa_pagamento(valor, user):
    notificador = NotificadorEmail()

    if valor > user.saldo:
        user.saldo -= valor
        notificador.notifica_pagamento(valor, user)
    else:
        raise ValueError("Saldo insuficiente")
```

O que vocês pensam sobre a rigidez e abstração dessa implementação?

---

### Dependências por Referência

- A função `processa_pagamento` possui uma **referência direta** à classe `NotificadorEmail`
- Nos testes nós teremos que **trocar esta referência**, em tempo de execução, para um mock que nós definimos
- Mas é importante lembrar de **voltar para o original** após os testes terminarem de rodar
- Quem controla isso para nós é o `mock.patch`
- Como a construção de `NotificadorEmail` parece simples, podemos **mockar apenas o seu método** `notifica_pagamento`

---

### Mockando somente o comportamento por referência

```python
def processa_pagamento(valor, user):
    notificador = NotificadorEmail()

    if valor > user.saldo:
        user.saldo -= valor
        notificador.notifica_pagamento(valor, user)
    else:
        raise ValueError("Saldo insuficiente")
```

```python
def test_processa_pagamento_com_sucesso_mock_object():
    user = User(saldo=500)

    with patch.object(NotificadorEmail, 'notifica_pagamento') as notifica:
        processa_pagamento(100, user)

        assert user.saldo == 400
        notifica.assert_called_once_with(100, user)
```

Mais chato né? Se tá chato de mockar, o design tá ruim.

---

### Comparando com a implementação injetando dependências

```python
def processa_pagamento(valor, user, notificador):
    if valor > user.saldo:
        user.saldo -= valor
        notificador.notifica_pagamento(valor, user)
    else:
        raise ValueError("Saldo insuficiente")
```

```python
def test_processa_pagamento_com_sucesso():
    user = User(saldo=500)
    notificador = Mock(spec=NotificadorEmail)

    processa_pagamento(100, user, notificador)

    assert user.saldo == 400
    notificador.notifica_pagamento.assert_called_once_with(100, user)
```

---

### Dependências por Referência mais rígidas
O caso que vimos é uma referência direta, ou seja, **rígida**, mas com uma **abstração mais alta** por ainda utilizar uma classe

Mas e se a implementação de `processa_pagamento` fosse a seguinte:

```python
def processa_pagamento(valor, user):
    if valor > user.saldo:
        user.saldo -= valor
        notifica_pagamento(valor, user)
    else:
        raise ValueError("Saldo insuficiente")
```

Agora, o código **não referencia uma classe, mas uma função** chamada `notifica_pagamento`.

---

### Mockando a referência por completo

```python
def processa_pagamento(valor, user):
    if valor > user.saldo:
        user.saldo -= valor
        notifica_pagamento(valor, user)
    else:
        raise ValueError("Saldo insuficiente")
```

```python
def test_processa_pagamento_com_sucesso_mock_object():
    user = User(saldo=500)

    with patch('app.services.pagamento.notifica_pagamento') as notifica:
        processa_pagamento(100, user)

        assert user.saldo == 400
        notifica.assert_called_once_with(100, user)
```

De todos as estratégias de mock, o `patch` simples é o que **evidencia o menor grau de abstração e mais alta rigidez** no código

---

# Concluindo
<!-- .slide: class="bg-green-pattern" -->

---

### Conclusões

- O **bom design se baseia em abstrações** e não em implementações (rigidez)
- Se um teste tem **muitos mocks**, isso mostra que o código está com um **alto acoplamento**
- Instâncias de `Mock` podem ser **melhor controladas** com o uso do `spec`
- O `patch` explicita a **rigidez e referências diretas** nas unidades de código testadas
- Use **injeção de dependência** para transformar referências rígidas em dependências abstratas
- **Evite ao máximo** mockar o Python (dunder methods, por exemplo) porque é chato e arriscado
- Existem outras nuâncias de mocks (exceções, retornos múltiplos) que não cobri nessa apresentação
