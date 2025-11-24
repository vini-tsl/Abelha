from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
from main import app
from models import db, Usuario, EstadoColmeia, Evidencia, SaudeAbelha, CapturaAbelha, ProducaoMel

# ================= FUNÇÕES AUXILIARES =================
def validar_email_institucional(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@academico\.ifpb\.edu\.br$'
    return re.match(pattern, email) is not None

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11

def validar_telefone(telefone):
    telefone = re.sub(r'\D', '', telefone)
    return len(telefone) >= 10  # Mais flexível para números com DDD

def validar_senha(senha):
    return len(senha) >= 6

def is_admin():
    return session.get('usuario_tipo') == 'Administrador'

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ================= ROTAS DE AUTENTICAÇÃO =================
@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('monitoramento'))
    return render_template('index.html')

@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    cpf = request.form['cpf']
    tipo_usuario = request.form['tipoUsuario']
    senha = request.form['senhaCadastro']
    confirma_senha = request.form['confirmaCadastro']
    
    # Validações
    erros = []
    
    if not nome or len(nome.strip()) < 2:
        erros.append('Nome deve ter pelo menos 2 caracteres')
    
    if not validar_email_institucional(email):
        erros.append('Email deve ser institucional (@academico.ifpb.edu.br)')
    
    if not validar_telefone(telefone):
        erros.append('Telefone inválido')
    
    if not validar_cpf(cpf):
        erros.append('CPF deve ter 11 dígitos')
    
    if not validar_senha(senha):
        erros.append('Senha deve ter pelo menos 6 caracteres')
    
    if senha != confirma_senha:
        erros.append('Senhas não coincidem')
    
    # Verificar se email ou CPF já existem
    if Usuario.query.filter_by(email=email).first():
        erros.append('Email já cadastrado')
    
    if Usuario.query.filter_by(cpf=cpf).first():
        erros.append('CPF já cadastrado')
    
    if tipo_usuario == 'Participante':
        matricula = request.form.get('matricula', '')
        if not matricula or len(re.sub(r'\D', '', matricula)) != 12:
            erros.append('Matrícula deve ter 12 dígitos')
    else:
        matricula = None
    
    if erros:
        for erro in erros:
            flash(erro, 'error')
        return render_template('index.html')
    
    # Criar usuário
    novo_usuario = Usuario(
        nome=nome.strip(),
        email=email.lower(),
        telefone=re.sub(r'\D', '', telefone),
        cpf=re.sub(r'\D', '', cpf),
        tipo_usuario=tipo_usuario,
        matricula=re.sub(r'\D', '', matricula) if matricula else None,
        senha=generate_password_hash(senha)
    )
    
    try:
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar usuário: {str(e)}', 'error')
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['emailLogin']
    senha = request.form['senhaLogin']
    
    usuario = Usuario.query.filter_by(email=email.lower(), ativo=True).first()
    
    if usuario and check_password_hash(usuario.senha, senha):
        session['usuario_id'] = usuario.id
        session['usuario_nome'] = usuario.nome
        session['usuario_tipo'] = usuario.tipo_usuario
        flash(f'Bem-vindo(a), {usuario.nome}!', 'success')
        return redirect(url_for('monitoramento'))
    else:
        flash('Email ou senha incorretos!', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

# ================= ROTAS DO SISTEMA =================

# Monitoramento - Alunos veem tudo, mas só apagam seus registros
@app.route('/monitoramento')
@login_required
def monitoramento():
    # Para ações (apagar) - usuário só vê seus próprios registros
    if is_admin():
        evidencias = Evidencia.query.order_by(Evidencia.data_registro.desc()).all()
    else:
        evidencias = Evidencia.query.filter_by(usuario_id=session['usuario_id']).order_by(Evidencia.data_registro.desc()).all()
    
    # Para visualização geral (todos podem ver tudo)
    todas_evidencias = Evidencia.query.order_by(Evidencia.data_registro.desc()).all()
    estado_colmeia = EstadoColmeia.query.order_by(EstadoColmeia.data_atualizacao.desc()).first()
    capturas = CapturaAbelha.query.order_by(CapturaAbelha.data_captura.desc()).all()
    registros_saude = SaudeAbelha.query.order_by(SaudeAbelha.data_registro.desc()).all()
    producoes_mel = ProducaoMel.query.order_by(ProducaoMel.data_registro.desc()).all()
    
    return render_template('monitoramento.html', 
                         evidencias=evidencias,
                         todas_evidencias=todas_evidencias,
                         estado_colmeia=estado_colmeia,
                         capturas=capturas,
                         registros_saude=registros_saude,
                         producoes_mel=producoes_mel,
                         is_admin=is_admin())

# Estado da Colmeia
@app.route('/estado-colmeia')
@login_required
def mostrar_estado_colmeia():
    if is_admin():
        estados = EstadoColmeia.query.order_by(EstadoColmeia.data_atualizacao.desc()).all()
    else:
        estados = EstadoColmeia.query.filter_by(usuario_id=session['usuario_id']).order_by(EstadoColmeia.data_atualizacao.desc()).all()
    
    estado_atual = EstadoColmeia.query.order_by(EstadoColmeia.data_atualizacao.desc()).first()
    todos_estados = EstadoColmeia.query.order_by(EstadoColmeia.data_atualizacao.desc()).all()
    
    return render_template('estado_colmeia.html', 
                         estados=estados, 
                         estado_atual=estado_atual,
                         todos_estados=todos_estados,
                         is_admin=is_admin())

# Captura de Abelhas
@app.route('/captura-abelhas')
@login_required
def mostrar_captura_abelha():
    if is_admin():
        capturas = CapturaAbelha.query.order_by(CapturaAbelha.data_captura.desc()).all()
    else:
        capturas = CapturaAbelha.query.filter_by(usuario_id=session['usuario_id']).order_by(CapturaAbelha.data_captura.desc()).all()
    
    todas_capturas = CapturaAbelha.query.order_by(CapturaAbelha.data_captura.desc()).all()
    return render_template('captura_abelhas.html', 
                         capturas=capturas,
                         todas_capturas=todas_capturas,
                         is_admin=is_admin())

# Saúde das Abelhas
@app.route('/saude-abelhas')
@login_required
def mostrar_saude_abelhas():
    if is_admin():
        registros_saude = SaudeAbelha.query.order_by(SaudeAbelha.data_registro.desc()).all()
    else:
        registros_saude = SaudeAbelha.query.filter_by(usuario_id=session['usuario_id']).order_by(SaudeAbelha.data_registro.desc()).all()
    
    todas_saude = SaudeAbelha.query.order_by(SaudeAbelha.data_registro.desc()).all()
    return render_template('saude_abelhas.html', 
                         registros_saude=registros_saude,
                         todas_saude=todas_saude,
                         is_admin=is_admin())

# Produção de Mel
@app.route('/producao-mel')
@login_required
def mostrar_producao_mel():
    if is_admin():
        producoes_mel = ProducaoMel.query.order_by(ProducaoMel.data_registro.desc()).all()
    else:
        producoes_mel = ProducaoMel.query.filter_by(usuario_id=session['usuario_id']).order_by(ProducaoMel.data_registro.desc()).all()
    
    todas_producoes = ProducaoMel.query.order_by(ProducaoMel.data_registro.desc()).all()
    return render_template('producao_mel.html', 
                         producoes_mel=producoes_mel,
                         todas_producoes=todas_producoes,
                         is_admin=is_admin())

# CONCLUSÃO - Nova página
@app.route('/conclusao')
@login_required
def conclusao():
    # Resumo Produção de Mel
    producoes = ProducaoMel.query.all()
    total_mel = sum(p.quantidade for p in producoes) if producoes else 0
    media_mel = total_mel / len(producoes) if producoes else 0
    ultima_producao = ProducaoMel.query.order_by(ProducaoMel.data_registro.desc()).first()
    
    # Resumo Saúde
    registros_saude = SaudeAbelha.query.all()
    media_atividade = sum(s.nivel_atividade or 0 for s in registros_saude) / len(registros_saude) if registros_saude else 0
    media_alimento = sum(s.presenca_alimento or 0 for s in registros_saude) / len(registros_saude) if registros_saude else 0
    
    # Resumo Capturas
    total_capturas = CapturaAbelha.query.count()
    todas_capturas = CapturaAbelha.query.order_by(CapturaAbelha.data_captura.desc()).all()
    
    # Resumo Estado Colmeia
    estado_atual = EstadoColmeia.query.order_by(EstadoColmeia.data_atualizacao.desc()).first()
    
    # Observações automáticas
    observacoes_finais = gerar_observacoes_automaticas(producoes, registros_saude, estado_atual)
    
    return render_template('conclusao.html',
                         total_mel=total_mel,
                         media_mel=media_mel,
                         ultima_producao=ultima_producao,
                         media_atividade=media_atividade,
                         media_alimento=media_alimento,
                         total_capturas=total_capturas,
                         todas_capturas=todas_capturas,
                         estado_atual=estado_atual,
                         observacoes_finais=observacoes_finais,
                         is_admin=is_admin())

def gerar_observacoes_automaticas(producoes, registros_saude, estado_atual):
    observacoes = []
    
    # Análise produção de mel
    if producoes:
        if len(producoes) >= 3:
            ultimas_producoes = sorted(producoes, key=lambda x: x.data_registro, reverse=True)[:3]
            tendencia = "estável"
            if ultimas_producoes[0].quantidade > ultimas_producoes[2].quantidade:
                tendencia = "crescendo"
            elif ultimas_producoes[0].quantidade < ultimas_producoes[2].quantidade:
                tendencia = "decaindo"
            observacoes.append(f"Produção de mel está {tendencia} nas últimas 3 colheitas")
        else:
            observacoes.append(f"Total de {len(producoes)} colheitas registradas")
    
    # Análise saúde
    if registros_saude:
        media_atividade = sum(s.nivel_atividade or 0 for s in registros_saude) / len(registros_saude)
        if media_atividade >= 7:
            observacoes.append("Alta atividade das abelhas indica colmeia saudável")
        elif media_atividade <= 4:
            observacoes.append("Baixa atividade requer atenção")
        else:
            observacoes.append("Atividade das abelhas dentro da média esperada")
    
    # Análise estado
    if estado_atual:
        if estado_atual.estado == 'alerta':
            observacoes.append("Colmeia em estado de alerta - intervenção necessária")
        else:
            observacoes.append("Colmeia em estado normal")
    
    if not observacoes:
        observacoes.append("Dados insuficientes para análise detalhada")
    
    return observacoes

# ================= ROTAS DE AÇÃO (com verificação de admin) =================

@app.route('/registrar-evidencia', methods=['POST'])
@login_required
def registrar_evidencia():
    descricao = request.form.get('descricaoEvidencia', '').strip()
    anotacoes = request.form.get('anotacoes', '').strip()
    
    if not descricao:
        flash('A descrição é obrigatória!', 'error')
        return redirect(url_for('monitoramento'))
    
    nova_evidencia = Evidencia(
        usuario_id=session['usuario_id'],
        descricao=descricao,
        anotacoes=anotacoes
    )
    
    try:
        db.session.add(nova_evidencia)
        db.session.commit()
        flash('Evidência registrada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao registrar evidência.', 'error')
    
    return redirect(url_for('monitoramento'))

@app.route('/excluir-evidencia/<int:id>', methods=['POST'])
@login_required
def excluir_evidencia(id):
    evidencia = Evidencia.query.get_or_404(id)
    
    # Verificar se é admin ou o dono do registro
    if not is_admin() and evidencia.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir este registro.', 'error')
        return redirect(url_for('monitoramento'))
    
    try:
        db.session.delete(evidencia)
        db.session.commit()
        flash('Evidência excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir evidência.', 'error')
    
    return redirect(url_for('monitoramento'))

@app.route('/salvar-estado-colmeia', methods=['POST'])
@login_required
def salvar_estado_colmeia():
    especie = request.form.get('especie', '').strip()
    peso = request.form.get('peso')
    contagem = request.form.get('contagem')
    observacoes = request.form.get('observacoes', '').strip()
    estado = request.form.get('estado', 'normal')
    
    novo_estado = EstadoColmeia(
        usuario_id=session['usuario_id'],
        especie=especie,
        peso=float(peso) if peso else None,
        contagem_abelhas=int(contagem) if contagem else None,
        observacoes=observacoes,
        estado=estado
    )
    
    try:
        db.session.add(novo_estado)
        db.session.commit()
        flash('Estado da colmeia salvo com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao salvar estado da colmeia.', 'error')
    
    return redirect(url_for('mostrar_estado_colmeia'))

@app.route('/excluir-estado-colmeia/<int:id>', methods=['POST'])
@login_required
def excluir_estado_colmeia(id):
    estado = EstadoColmeia.query.get_or_404(id)
    
    if not is_admin() and estado.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir este registro.', 'error')
        return redirect(url_for('mostrar_estado_colmeia'))
    
    try:
        db.session.delete(estado)
        db.session.commit()
        flash('Estado da colmeia excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir estado da colmeia.', 'error')
    
    return redirect(url_for('mostrar_estado_colmeia'))

@app.route('/registrar-captura', methods=['POST'])
@login_required
def registrar_captura():
    observacao = request.form.get('observacaoCaptura', '').strip()
    
    if not observacao:
        flash('A observação é obrigatória!', 'error')
        return redirect(url_for('mostrar_captura_abelha'))
    
    nova_captura = CapturaAbelha(
        usuario_id=session['usuario_id'],
        observacao=observacao
    )
    
    try:
        db.session.add(nova_captura)
        db.session.commit()
        flash('Captura registrada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao registrar captura.', 'error')
    
    return redirect(url_for('mostrar_captura_abelha'))

@app.route('/excluir-captura/<int:id>', methods=['POST'])
@login_required
def excluir_captura(id):
    captura = CapturaAbelha.query.get_or_404(id)
    
    if not is_admin() and captura.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir este registro.', 'error')
        return redirect(url_for('mostrar_captura_abelha'))
    
    try:
        db.session.delete(captura)
        db.session.commit()
        flash('Captura excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir captura.', 'error')
    
    return redirect(url_for('mostrar_captura_abelha'))

@app.route('/registrar-saude', methods=['POST'])
@login_required
def registrar_saude():
    nivel_atividade = request.form.get('nivelAtividade')
    presenca_alimento = request.form.get('presencaAlimento')
    abelhas_visiveis = request.form.get('abelhasVisiveis')
    pregas_problemas = request.form.get('pregasProblemas', '').strip()
    observacoes_gerais = request.form.get('observacoesGerais', '').strip()
    
    novo_registro = SaudeAbelha(
        usuario_id=session['usuario_id'],
        nivel_atividade=int(nivel_atividade) if nivel_atividade else None,
        presenca_alimento=int(presenca_alimento) if presenca_alimento else None,
        abelhas_visiveis=int(abelhas_visiveis) if abelhas_visiveis else None,
        pregas_problemas=pregas_problemas,
        observacoes_gerais=observacoes_gerais
    )
    
    try:
        db.session.add(novo_registro)
        db.session.commit()
        flash('Registro de saúde salvo com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao salvar registro de saúde.', 'error')
    
    return redirect(url_for('mostrar_saude_abelhas'))

@app.route('/excluir-saude/<int:id>', methods=['POST'])
@login_required
def excluir_saude(id):
    registro = SaudeAbelha.query.get_or_404(id)
    
    if not is_admin() and registro.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir este registro.', 'error')
        return redirect(url_for('mostrar_saude_abelhas'))
    
    try:
        db.session.delete(registro)
        db.session.commit()
        flash('Registro de saúde excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir registro de saúde.', 'error')
    
    return redirect(url_for('mostrar_saude_abelhas'))

@app.route('/registrar-producao-mel', methods=['POST'])
@login_required
def registrar_producao_mel():
    quantidade = request.form.get('quantidadeMel')
    data_colheita = request.form.get('dataMel')
    observacoes = request.form.get('observacoesMel', '').strip()
    
    if not quantidade or not data_colheita:
        flash('Quantidade e data da colheita são obrigatórios!', 'error')
        return redirect(url_for('mostrar_producao_mel'))
    
    try:
        nova_producao = ProducaoMel(
            usuario_id=session['usuario_id'],
            quantidade=float(quantidade),
            data_colheita=datetime.strptime(data_colheita, '%Y-%m-%d').date(),
            observacoes=observacoes
        )
        
        db.session.add(nova_producao)
        db.session.commit()
        flash('Produção de mel registrada com sucesso!', 'success')
    except ValueError:
        flash('Quantidade deve ser um número válido!', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao registrar produção de mel.', 'error')
    
    return redirect(url_for('mostrar_producao_mel'))

@app.route('/excluir-producao-mel/<int:id>', methods=['POST'])
@login_required
def excluir_producao_mel(id):
    producao = ProducaoMel.query.get_or_404(id)
    
    if not is_admin() and producao.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir este registro.', 'error')
        return redirect(url_for('mostrar_producao_mel'))
    
    try:
        db.session.delete(producao)
        db.session.commit()
        flash('Produção de mel excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir produção de mel.', 'error')
    
    return redirect(url_for('mostrar_producao_mel'))

# Rota para administradores gerenciarem usuários
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not is_admin():
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('monitoramento'))
    
    usuarios = Usuario.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/toggle-usuario/<int:id>')
@login_required
def toggle_usuario(id):
    if not is_admin():
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('monitoramento'))
    
    usuario = Usuario.query.get_or_404(id)
    usuario.ativo = not usuario.ativo
    
    try:
        db.session.commit()
        status = "ativado" if usuario.ativo else "desativado"
        flash(f'Usuário {usuario.nome} {status} com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao alterar status do usuário.', 'error')
    
    return redirect(url_for('admin_usuarios'))