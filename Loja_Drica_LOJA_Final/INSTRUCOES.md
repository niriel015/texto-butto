# Hyper Femme — LOJA publica (download separado)

**Link local:** `http://127.0.0.1:8000/`.

1. Extraia o ZIP em `Downloads`.
2. Dê duplo clique em `01_PREPARAR_LOJA.bat` (instala Python/Django, reutiliza as credenciais locais e faz migrações, sem apagar dados existentes).
3. Execute `02_INICIAR_LOJA.bat` para abrir a loja.
4. Abra o endereco no Chrome.

Aqui ficam apenas as telas publicas: vitrine, carrinho, contas e pedidos. **Não há rotas de administração nesta aplicação.** Para cadastrar produtos e alterar o visual, use o download separado do painel.

## Como ficam conectados

Os dois downloads sao PROJETOS SEPARADOS: cada um inicia seu proprio Django, em uma porta propria.
Ambos utilizam o MESMO PostgreSQL configurado em `%USERPROFILE%\HyperFemmeCompartilhado\.env`, e as MESMAS fotos em `%USERPROFILE%\HyperFemmeCompartilhado\media`.

Se sua Hyper Store antiga estiver em `Downloads\hyper_store_codigo_fonte\hyper_store`, o configurador importa automaticamente o `.env` privado antigo e copia as fotos ainda ausentes. Nao apaga o banco e nao inclui suas credenciais no ZIP. Se o arquivo antigo nao estiver ali, sera preciso ajustar `DATABASE_URL` uma vez no arquivo compartilhado.

**O que nao foi validado:** conexao real ao PostgreSQL do seu PC, testes automatizados do Django, pagamento real Mercado Pago. Este servidor e para testes locais, nao para abrir vendas reais na internet. Para producao configure HTTPS, servidor profissional, armazenamento de imagens compartilhado, backups e pagamentos homologados.

**Seguranca:** o `.env` compartilhado contem senhas; nao o envie nem compartilhe prints. Alterar a senha do PostgreSQL no banco exige atualizar a mesma `DATABASE_URL` compartilhada. A senha mostrada nas imagens anteriores deve ser trocada antes de publicar.
