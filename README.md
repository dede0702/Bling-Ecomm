Alan de Souza Maximiano - RM557088

André Rovai Jr          - RM555848

Pedro Henrique Conte    - RM554987

Lancelot Chagas         - RM554707

Kauan Alves             - RM555082


# Sistema de Gestão de Estoque e Vendas

Este projeto é uma aplicação web desenvolvida em Flask para gerenciar inventário e vendas de produtos. A aplicação permite autenticação de usuários, manipulação de produtos e emissão de relatórios de estoque, além de estar preparada para futuras melhorias, incluindo um aplicativo móvel para leitura de código de barras.

## Funcionalidades Principais

- *Autenticação de Usuários:*
  - Login seguro com hashing de senhas.
  - Registro de novos usuários com verificação de e-mail duplicado.

- *Gestão de Produtos:*
  - Visualização, adição, edição e exclusão de produtos.
  - Manutenção de histórico de preços e controle de mínimas quantidades de estoque.

- *Controle de Estoque:*
  - Registro de vendas de produtos com ajuste automático de inventário.
  - Alertas para produtos com estoque baixo de acordo com um mínimo estipulado.

- *Relatórios e Exportações:*
  - Emissão de relatórios de produtos e vendas em formato CSV.

## Melhorias Planejadas

### 1. Integração com Código de Barras

- *Aplicativo Móvel:*
  - Desenvolvimento de um app móvel para leitura de códigos de barras usando Flutter ou React Native.
  - Comunicação via API com o backend para atualização de estoque em tempo real.

- *Compatibilidade com Dispositivos USB:*
  - Suporte para leitores de código de barras USB usados em desktop.

### 2. Segurança e Gestão de Usuários

- *OAuth/ JWT Autenticação:*
  - Implementação de sistemas de token para melhor segurança.
  - Gerenciamento de permissões para controle de acesso baseado em funções de usuário.

### 3. Experiência de Usuário

- *Redesign de UI/UX:*
  - Atualização do design visual para melhorar a usabilidade.
  - Garantia de que a aplicação é totalmente responsiva.

### 4. Dados e Relatórios

- *Banco de Dados Relacional:*
  - Migração para banco de dados como PostgreSQL para melhor escalabilidade e performance.

- *Relatórios Detalhados:*
  - Funcionalidades avançadas para criação de relatórios customizados.

 5. Automação e Notificações

- *Alertas de Estoque:*
  - Notificação por e-mail ou push para produtos com estoque abaixo do mínimo desejado.

- *Integração com Fornecedores:*
  - APIs para atualização automática de inventário e preços.

Como Contribuir

1. Faça um fork do repositório.
2. Crie uma nova branch para sua funcionalidade (git checkout -b sua-feature).
3. Commit suas alterações (git commit -m 'Descrição das mudanças').
4. Faça o push para a branch (git push origin sua-feature).
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
