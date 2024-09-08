import csv  # Manipulação de arquivos CSV
import io  # Operações de entrada e saída (streams de dados)
from functools import wraps  # Manter metadados em decorators
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file  # Framework web Flask e funções relacionadas
from werkzeug.security import generate_password_hash, check_password_hash  # Hash e verificação de senhas
import locale  # Configurações regionais para formatação de dados

app = Flask(__name__)  # Cria a aplicação Flask
app.secret_key = 'sua_chave_secreta_aqui'  # Define a chave secreta usada para sessões e mensagens flash

# Simulação de banco de dados em memória (para exemplo)
users_db = {}

# Definir locale para o Brasil (moeda)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para garantir que o usuário esteja logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Função para carregar os produtos do arquivo vendas.csv
def carregar_produtos():
    produtos = []
    try:
        with open('vendas.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Verificar se o campo 'Valor Unitário' existe e tentar converter
                try:
                    row['Valor Unitário'] = float(
                        row['Valor Unitário'].replace('R$', '').replace('.', '').replace(',', '.'))
                except (ValueError, KeyError):
                    row['Valor Unitário'] = 0.00  # Valor padrão em caso de erro de conversão

                # Adicionar a verificação do estoque
                try:
                    quantidade = int(row['Quantidade'])
                    estoque_minimo = int(row.get('Estoque Mínimo', 0))  # Novo campo 'Estoque Mínimo'
                except (ValueError, KeyError):
                    quantidade = 0
                    estoque_minimo = 0

                # Define o status do estoque
                if quantidade <= estoque_minimo:
                    row['status_estoque'] = 'baixo'  # Estoque baixo
                else:
                    row['status_estoque'] = 'ok'  # Estoque ok

                produtos.append(row)
    except FileNotFoundError:
        flash('Arquivo vendas.csv não encontrado.', 'danger')
    except Exception as e:
        flash(f'Ocorreu um erro ao carregar os produtos: {e}', 'danger')

    return produtos

# Página inicial (requer login)
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/adicionar_responsavel', methods=['POST'])
@login_required
def adicionar_responsavel():
    nome = request.form['nome']
    # Adicione lógica para salvar o nome do responsável (banco de dados, arquivo, etc.)
    flash(f'Responsável {nome} adicionado com sucesso!', 'success')
    return redirect(url_for('painel_principal'))

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_db.get(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('produtos'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')

    return render_template('login.html')

# Página de cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if password != password_confirm:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('register'))

        if email in users_db:
            flash('E-mail já registrado.', 'danger')
            return redirect(url_for('register'))

        # Criando novo usuário
        user_id = len(users_db) + 1
        hashed_password = generate_password_hash(password)
        users_db[email] = {'id': user_id, 'nome': nome, 'email': email, 'password': hashed_password}

        flash('Cadastro realizado com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Rota para Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login'))

# Página de visualização de vendas (requer login)
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Definindo locale para Brasil

@app.route('/vendas', methods=['GET', 'POST'])
@login_required
def vendas():
    produtos = carregar_produtos()
    vendas_filtradas = []

    produto_filtrado = request.args.get('produto')

    # Filtrar produtos
    for produto in produtos:
        if not produto_filtrado or produto['Produto'] == produto_filtrado:
            try:
                valor_unitario = float(produto['Valor Unitário'])  # Convertendo para float
            except ValueError:
                valor_unitario = 0.0  # Se o valor for inválido, definir como 0.0

            vendas_filtradas.append({
                'Coluna 1': produto['Produto'],
                'Coluna 2': produto['Quantidade'],
                'Coluna 3': valor_unitario,
                'Coluna 4': produto['Categoria'],
                'Coluna 5': produto['Marca'],
            })

    # Calcula o total
    total = 0
    for venda in vendas_filtradas:
        try:
            quantidade = int(venda['Coluna 2'])
            preco = venda['Coluna 3']  # Já convertido para float anteriormente
            total += quantidade * preco
        except ValueError as e:
            flash(f"Erro ao calcular o total para {venda['Coluna 1']}: {e}", 'danger')

    # Formatar o total para exibição como moeda
    total_formatado = locale.currency(total, grouping=True)

    # Formatar valores de cada venda para exibição como moeda
    for venda in vendas_filtradas:
        try:
            venda['Coluna 3'] = locale.currency(venda['Coluna 3'], grouping=True)  # Formatando como moeda para exibição
        except ValueError:
            venda['Coluna 3'] = "R$ 0,00"  # Se o valor for inválido

    return render_template('vendas-2.html', vendas=vendas_filtradas, total=total_formatado, produtos=produtos)

# Página de gestão de produtos (requer login)
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Define locale para Brasil

import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Define locale para Brasil

# Definição da função formatar_moeda
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Rota para a pagina de produtos
@app.route('/produtos', methods=['GET', 'POST'])
@login_required
def produtos():
    produtos = carregar_produtos()

    # Formatar o valor unitário como moeda para exibição
    for produto in produtos:
        try:
            valor_unitario = float(produto['Valor Unitário'])
            produto['Valor Unitário'] = formatar_moeda(valor_unitario)

            # Verifica o estoque mínimo e aplica a cor de alerta
            quantidade = int(produto['Quantidade'])
            estoque_minimo = int(produto.get('Estoque Mínimo', 0))  # Pega o valor do estoque mínimo

            # Define o status de estoque (vermelho para baixo e verde para ok)
            produto['status_estoque'] = 'baixo' if quantidade <= estoque_minimo else 'ok'

        except (ValueError, KeyError):
            produto['Valor Unitário'] = "R$ 0,00"  # Exibir como R$ 0,00 em caso de erro

    return render_template('produtos.html', vendas=produtos)

# Rota para a pagina de alteração de preços.
@app.route('/alterar_preco', methods=['POST'])
@login_required
def alterar_preco():
    if request.method == 'POST':
        # Captura os dados do formulário
        codigo_produto = request.form['codigo_produto']
        novo_preco = request.form['novo_preco']

        # Carrega os produtos do CSV
        try:
            # Abre o arquivo para leitura
            with open('vendas.csv', 'r', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Produto', 'Código do Produto', 'Descrição', 'Quantidade', 'Valor Unitário', 'Categoria', 'Marca', 'Característica']
                reader = csv.DictReader(csvfile, fieldnames=fieldnames)
                rows = list(reader)  # Ler todas as linhas

            # Modifica o preço do produto correspondente
            for row in rows:
                if row['Código do Produto'] == codigo_produto:
                    row['Valor Unitário'] = novo_preco

            # Abre o arquivo para escrita e reescrever o CSV com os preços atualizados
            with open('vendas.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # Escrever o cabeçalho
                writer.writerows(rows)  # Escrever os dados modificados

            flash('Preço alterado com sucesso!', 'success')
        except Exception as e:
            flash(f'Ocorreu um erro ao alterar o preço: {e}', 'danger')

        return redirect(url_for('produtos'))

# Rota para a pagina de editar produtos
@app.route('/editar_produto/<produto_nome>', methods=['GET', 'POST'])  # Define a rota para editar um produto, permitindo GET e POST
@login_required  # Requer login para acessar a função
def editar_produto(produto_nome):  # Função para editar um produto com base no nome fornecido
    produtos = carregar_produtos()  # Carrega a lista de produtos
    produto = next((p for p in produtos if p['Produto'] == produto_nome), None)  # Busca o produto pelo nome

    if produto is None:  # Se o produto não for encontrado
        flash('Produto não encontrado.', 'danger')  # Exibe uma mensagem de erro
        return redirect(url_for('produtos'))  # Redireciona para a página de produtos

    if request.method == 'POST':  # Se o método for POST (ao enviar o formulário)
        novo_nome = request.form['novo_nome']  # Obtém o novo nome do produto
        novo_preco = request.form['novo_preco']  # Obtém o novo preço do produto

        for p in produtos:  # Percorre a lista de produtos
            if p['Produto'] == produto_nome:  # Encontra o produto a ser editado
                p['Produto'] = novo_nome  # Atualiza o nome do produto
                p['Valor Unitário'] = novo_preco  # Atualiza o preço do produto
                break  # Encerra o loop após a atualização

        # Abre o arquivo CSV em modo de escrita, para atualizar os dados
        with open('vendas.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Produto', 'Código do Produto', 'Descrição', 'Quantidade', 'Valor Unitário', 'Categoria',
                          'Marca', 'Característica']  # Define os campos do CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # Prepara o writer para escrever no CSV
            writer.writeheader()  # Escreve o cabeçalho no arquivo
            writer.writerows(produtos)  # Escreve os dados atualizados dos produtos

        flash(f'Produto {novo_nome} atualizado com sucesso!', 'success')  # Exibe uma mensagem de sucesso
        return redirect(url_for('produtos'))  # Redireciona para a página de produtos

    return render_template('editar_produto.html', produto=produto)  # Renderiza o template para editar o produto

# Rota para a pagina de adicionar produto
@app.route('/adicionar_produto', methods=['GET', 'POST'])
@login_required
def adicionar_produto():
    if request.method == 'POST':
        # Capturar os dados do formulário
        nome = request.form['nome']
        codigo = request.form['codigo']
        descricao = request.form.get('descricao', '')
        preco = request.form['preco']
        quantidade = request.form.get('quantidade', 0)
        estoque_minimo = request.form.get('estoque_minimo', 0)  # Novo campo para o estoque mínimo
        categoria = request.form.get('categoria', '')
        marca = request.form.get('marca', '')
        caracteristica = request.form.get('caracteristica', '')

        # Valida e formatar o preço e a quantidade
        try:
            preco = float(preco)
            quantidade = int(quantidade)
            estoque_minimo = int(estoque_minimo)
        except ValueError:
            flash('Valores inválidos.', 'danger')
            return redirect(url_for('adicionar_produto'))

        # Adicionar ao arquivo CSV
        try:
            with open('vendas.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Produto', 'Código do Produto', 'Descrição', 'Quantidade', 'Valor Unitário', 'Estoque Mínimo', 'Categoria', 'Marca', 'Característica']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({
                    'Produto': nome,
                    'Código do Produto': codigo,
                    'Descrição': descricao,
                    'Quantidade': quantidade,
                    'Valor Unitário': f"R$ {preco:.2f}",
                    'Estoque Mínimo': estoque_minimo,  # Adiciona o estoque mínimo ao CSV
                    'Categoria': categoria,
                    'Marca': marca,
                    'Característica': caracteristica
                })
            flash('Novo produto adicionado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao salvar o produto: {e}', 'danger')

        return redirect(url_for('produtos'))

    return render_template('adicionar_produto.html')

# Rota para a pagina vender produto

@app.route('/vender_produto', methods=['GET', 'POST'])
@login_required
def vender_produto():
    produtos = carregar_produtos()

    if request.method == 'POST':
        produto_nome = request.form['produto']
        try:
            quantidade_vendida = int(request.form['quantidade'])
        except ValueError:
            flash('Quantidade inválida.', 'danger')
            return redirect(url_for('vender_produto'))

        # Procura o produto no CSV
        produto = next((p for p in produtos if p['Produto'] == produto_nome), None)

        if produto:
            try:
                estoque_atual = int(produto['Quantidade'])
            except ValueError:
                flash('Erro no formato de quantidade do estoque.', 'danger')
                return redirect(url_for('vender_produto'))

            if quantidade_vendida <= 0:
                flash('A quantidade vendida deve ser maior que zero.', 'danger')
            elif quantidade_vendida > estoque_atual:
                flash('Quantidade vendida é maior que a disponível em estoque.', 'danger')
            else:
                # Atualiza a quantidade do produto
                produto['Quantidade'] = str(estoque_atual - quantidade_vendida)

                # Salva as alterações no CSV (modo 'w' para reescrever o arquivo)
                try:
                    with open('vendas.csv', 'a', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['Produto', 'Código do Produto', 'Descrição', 'Quantidade', 'Valor Unitário', 'Categoria', 'Marca', 'Característica']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()  # Escreve o cabeçalho apenas uma vez
                        writer.writerows(produtos)  # Escreve todos os produtos atualizados

                    flash(f'Venda de {quantidade_vendida} unidades do produto {produto_nome} realizada com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao salvar as alterações no arquivo: {e}', 'danger')

                return redirect(url_for('vender_produto'))

    return render_template('vender_produto.html', produtos=produtos)

# Rota para emitir o arquivo CSV.
@app.route('/emitir_csv')
@login_required
def emitir_csv():
    # Carregar todos os produtos
    produtos = carregar_produtos()

    # Simulando um arquivo CSV em memória
    output = io.StringIO()
    fieldnames = ['Código do Produto', 'Produto', 'Descrição', 'Quantidade', 'Valor Unitário', 'Categoria', 'Marca', 'Garantia']

    # Criando o writer para escrever no StringIO
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')  # Use 'ignore' para evitar erros
    writer.writeheader()

    # Ajuste seus produtos para adicionar campos como 'Código do Produto' se necessário
    for p in produtos:
        p['Código do Produto'] = p.get('Código do Produto', '')  # Adicionando um código, se não estiver presente

    writer.writerows(produtos)  # Escreve todas as linhas dos produtos no arquivo CSV

    output.seek(0)  # Mover para o início do arquivo

    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), as_attachment=True, download_name='produtos_em_estoque.csv', mimetype='text/csv')

if __name__ == "__main__":  # Verifica se o script está sendo executado diretamente
    app.run(debug=True)  # Inicia o servidor Flask com o modo debug ativado para desenvolvimento
