 /* ================== VARIÁVEIS ================== */
        let codigoGerado = "";
        const registros = [];
        const capturas = [];
        const registrosSaude = [];
        const registrosMel = [];
        const estadoColmeia = {
            especie: "", peso: "", contagem: "", observacoes: "", estado: "normal",
            atualizacoes: { especie: "", peso: "", contagem: "", observacoes: "", estado: "" }
        };

        /* ================== HELPERS ================== */
        function agoraStr() {
            const d = new Date();
            const dia = String(d.getDate()).padStart(2,'0');
            const mes = String(d.getMonth()+1).padStart(2,'0');
            const ano = d.getFullYear();
            const hora = String(d.getHours()).padStart(2,'0');
            const min = String(d.getMinutes()).padStart(2,'0');
            const seg = String(d.getSeconds()).padStart(2,'0');
            return `${dia}/${mes}/${ano} ${hora}:${min}:${seg}`;
        }
        
        function soNumeros(v) { return (v||"").replace(/\D+/g,""); }
        
        function validarNome(v){ return v && /^[A-Za-zÀ-ÖØ-öø-ÿ'’´`^~.\- ]{2,}$/.test(v.trim()) && !/\d/.test(v); }
        
        function validarEmail(v){ return v && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()); }
        
        function validarTelefone(v){ return soNumeros(v).length === 11; }
        
        function validarCPF(v){
            const d = soNumeros(v); if(d.length!==11 || /^(\d)\1{10}$/.test(d)) return false;
            let soma=0; for(let i=0;i<9;i++) soma+=parseInt(d[i])*(10-i); let resto=soma%11; let dv1=(resto<2?0:11-resto); if(dv1!==parseInt(d[9])) return false;
            soma=0; for(let i=0;i<10;i++) soma+=parseInt(d[i])*(11-i); resto=soma%11; let dv2=(resto<2?0:11-resto); if(dv2!==parseInt(d[10])) return false;
            return true;
        }
        
        function validarSenhaForte(s){ return s && s.length>=6 && /[A-Za-z]/.test(s) && /\d/.test(s); }
        
        function validarSenhaSimples(s){ return s && s.length>=6; }

        /* ================== TROCA DE TELAS ================== */
        function esconderTodasTelas(){
            const telas=["monitoramento","estadoColmeia","capturaAbelha","saudeAbelhas","producaoMel"];
            telas.forEach(t=>document.getElementById(t).classList.add("hidden"));
        }
        

        
        function mostrarRecuperar(){
            esconderTodasTelas(); document.getElementById("recuperar").classList.remove("hidden");
            document.getElementById("etapa1").classList.remove("hidden");
            document.getElementById("etapa2").classList.add("hidden");
            document.getElementById("etapa3").classList.add("hidden");
            document.getElementById("erroEmailRecuperar").textContent="";
            document.getElementById("erroCodigo").textContent="";
        }
        
        function mostrarMonitoramento(){ window.location.href = 'monitoramento.html';}
        
        function mostrarEstadoColmeia(){ esconderTodasTelas(); document.getElementById("estadoColmeia").classList.remove("hidden"); renderEstadoVisual(); renderCapturas(); }
        
        function mostrarCapturaAbelha(){ esconderTodasTelas(); document.getElementById("capturaAbelha").classList.remove("hidden"); }
        
        function mostrarSaudeAbelhas(){ esconderTodasTelas(); document.getElementById("saudeAbelhas").classList.remove("hidden"); }
        
        function mostrarProducaoMel(){ esconderTodasTelas(); document.getElementById("producaoMel").classList.remove("hidden"); }

        /* ================== NOTIFICAÇÃO & TOGGLE ================== */
        function toggleSenha(id){ const c=document.getElementById(id); c.type=c.type==="password"?"text":"password"; }
        
        function mostrarNotificacao(msg){
            const n=document.createElement("div"); n.className="notificacao"; n.textContent=msg; document.body.appendChild(n);
            setTimeout(()=>n.remove(),6000);
        }

        /* ================== CADASTRO ================== */
        function verificarTipo(){
            const tipo=document.getElementById("tipoUsuario").value;
            const divMatricula=document.getElementById("divMatricula");
            if(tipo==="Participante"){divMatricula.classList.remove("hidden");}else{divMatricula.classList.add("hidden");}
        }
        
        function cadastrar() {
            let valido = true;
            const nome = document.getElementById("nome").value;
            const email = document.getElementById("email").value;
            const telefone = document.getElementById("telefone").value;
            const cpf = document.getElementById("cpf").value;
            const tipo = document.getElementById("tipoUsuario").value;
            const matricula = document.getElementById("matricula").value;
            const senha = document.getElementById("senhaCadastro").value;
            const confirma = document.getElementById("confirmaCadastro").value;

            // limpa erros
            ["erroNome","erroEmail","erroTelefone","erroCPF","erroTipo","erroMatricula","erroSenhaCadastro","erroConfirmaCadastro"]
            .forEach(id=>document.getElementById(id).textContent="");

            if(!validarNome(nome)){ document.getElementById("erroNome").textContent="Nome inválido!"; valido=false; }
            if(!validarEmail(email)){ document.getElementById("erroEmail").textContent="E-mail inválido!"; valido=false; }
            if(!validarTelefone(telefone)){ document.getElementById("erroTelefone").textContent="Telefone deve ter 11 dígitos"; valido=false; }
            if(!validarCPF(cpf)){ document.getElementById("erroCPF").textContent="CPF inválido"; valido=false; }
            if(tipo==="-- Selecione --"){ document.getElementById("erroTipo").textContent="Selecione um tipo de usuário."; valido=false; }
            if(tipo==="Participante"){ if(soNumeros(matricula).length!==12){ document.getElementById("erroMatricula").textContent="Matrícula deve ter 12 dígitos"; valido=false; } }
            if(!validarSenhaForte(senha)){ document.getElementById("erroSenhaCadastro").textContent="Senha deve ter letras e números (mín.6)."; valido=false; }
            if(senha!==confirma){ document.getElementById("erroConfirmaCadastro").textContent="Senhas não coincidem"; valido=false; }

            if(valido){ mostrarNotificacao("Cadastro realizado com sucesso!"); mostrarMonitoramento(); }
        }

        /* ================== LOGIN ================== */
        function entrar(){
            const email=document.getElementById("emailLogin").value;
            const senha=document.getElementById("senhaLogin").value;
            document.getElementById("erroEmailLogin").textContent="";
            document.getElementById("erroSenhaLogin").textContent="";
            if(!validarEmail(email)){document.getElementById("erroEmailLogin").textContent="E-mail inválido!"; return;}
            if(!validarSenhaSimples(senha)){document.getElementById("erroSenhaLogin").textContent="Senha inválida"; return;}
            mostrarNotificacao("Login realizado com sucesso!");
            mostrarMonitoramento();
        }

        /* ================== RECUPERAR SENHA ================== */
        function enviarCodigo(){
            const email=document.getElementById("emailRecuperar").value;
            document.getElementById("erroEmailRecuperar").textContent="";
            if(!validarEmail(email)){document.getElementById("erroEmailRecuperar").textContent="E-mail inválido!"; return;}
            codigoGerado=Math.floor(100000+Math.random()*900000).toString();
            mostrarNotificacao("Código enviado: "+codigoGerado);
            document.getElementById("etapa1").classList.add("hidden");
            document.getElementById("etapa2").classList.remove("hidden");
            document.getElementById("erroCodigo").textContent="";
        }
        
        function verificarCodigo(){
            const codigoDigitado=document.getElementById("codigoInput").value.trim();
            document.getElementById("erroCodigo").textContent="";
            if(!codigoGerado){ document.getElementById("erroCodigo").textContent="Envie o código primeiro."; return;}
            if(codigoDigitado!==codigoGerado){ document.getElementById("erroCodigo").textContent="Código incorreto!"; return;}
            mostrarNotificacao("Código verificado!");
            document.getElementById("etapa2").classList.add("hidden");
            document.getElementById("etapa3").classList.remove("hidden");
        }
        
        function redefinirSenha(){
            const nova=document.getElementById("novaSenha").value;
            const conf=document.getElementById("confirmarSenha").value;
            document.getElementById("erroNovaSenha").textContent="";
            document.getElementById("erroConfirmaSenha").textContent="";
            if(!validarSenhaForte(nova)){ document.getElementById("erroNovaSenha").textContent="Senha inválida"; return; }
            if(nova!==conf){ document.getElementById("erroConfirmaSenha").textContent="Senhas não coincidem"; return; }
            mostrarNotificacao("Senha redefinida com sucesso!");
            codigoGerado="";
            document.getElementById("etapa3").classList.add("hidden");
            mostrarLogin();
        }

        /* ================== MONITORAMENTO ================== */
        function registrarEvidencia(){
            const descricao=document.getElementById("descricaoEvidencia").value.trim();
            const anotacoes=document.getElementById("anotacoes").value.trim();
            const foto=document.getElementById("foto").files[0]?document.getElementById("foto").files[0].name:"";
            const video=document.getElementById("video").files[0]?document.getElementById("video").files[0].name:"";
            const audio=document.getElementById("audio").files[0]?document.getElementById("audio").files[0].name:"";
            const data=new Date();
            registros.push({descricao,anotacoes,foto,video,audio,data});
            atualizarRegistros();
            document.getElementById("descricaoEvidencia").value="";
            document.getElementById("anotacoes").value="";
            document.getElementById("foto").value="";
            document.getElementById("video").value="";
            document.getElementById("audio").value="";
        }
        
        function atualizarRegistros(){
            const container=document.getElementById("registros");
            container.innerHTML="";
            registros.forEach((reg,index)=>{
                const div=document.createElement("div");
                div.className="registro";
                div.innerHTML=`<strong>Data/Hora:</strong> ${reg.data.toLocaleString()}<br>
                <strong>Descrição:</strong> ${reg.descricao||"(vazio)"}<br>
                <strong>Anotações:</strong> ${reg.anotacoes||"(vazio)"}<br>
                <strong>Foto:</strong> ${reg.foto||"(nenhuma)"}<br>
                <strong>Vídeo:</strong> ${reg.video||"(nenhum)"}<br>
                <strong>Áudio:</strong> ${reg.audio||"(nenhum)"}<button onclick="apagarRegistro(${index})">Apagar</button>`;
                container.appendChild(div);
            });
        }
        
        function apagarRegistro(index){ registros.splice(index,1); atualizarRegistros(); }
        
        /* ================== ESTADO DA COLMEIA ================== */
        function atualizarEstadoColmeia(){
            const especie=document.getElementById("especie").value.trim();
            const peso=document.getElementById("peso").value.trim();
            const contagem=document.getElementById("contagem").value.trim();
            const observacoes=document.getElementById("observacoes").value.trim();
            const estado=document.getElementById("estadoColmeiaInput").value;

            estadoColmeia.especie=especie;
            estadoColmeia.peso=peso;
            estadoColmeia.contagem=contagem;
            estadoColmeia.observacoes=observacoes;
            estadoColmeia.estado=estado;

            renderEstadoVisual();
            mostrarNotificacao("Estado da colmeia atualizado!");
        }

        function renderEstadoVisual(){
            const container=document.getElementById("visualColmeia");
            container.innerHTML=`<strong>Espécie:</strong> ${estadoColmeia.especie||"(vazio)"}<br>
            <strong>Peso:</strong> ${estadoColmeia.peso||"(vazio)"}<br>
            <strong>Contagem:</strong> ${estadoColmeia.contagem||"(vazio)"}<br>
            <strong>Observações:</strong> ${estadoColmeia.observacoes||"(vazio)"}<br>
            <strong>Estado:</strong> ${estadoColmeia.estado}`;
        }

        /* ================== CAPTURA DE ABELHAS ================== */
        function registrarCaptura(){
            const tipo=document.getElementById("tipoAbelha").value.trim();
            const quantidade=document.getElementById("quantidade").value.trim();
            const data=new Date();
            if(!tipo || !quantidade || isNaN(quantidade)){ alert("Preencha corretamente"); return; }
            capturas.push({tipo,quantidade,data});
            renderCapturas();
            document.getElementById("tipoAbelha").value="";
            document.getElementById("quantidade").value="";
            mostrarNotificacao("Captura registrada!");
        }

        function renderCapturas(){
            const container=document.getElementById("listaCapturas");
            container.innerHTML="";
            capturas.forEach((cap,index)=>{
                const div=document.createElement("div");
                div.className="registro";
                div.innerHTML=`<strong>Data/Hora:</strong> ${cap.data.toLocaleString()}<br>
                <strong>Tipo:</strong> ${cap.tipo}<br>
                <strong>Quantidade:</strong> ${cap.quantidade}<br>
                <button onclick="apagarCaptura(${index})">Apagar</button>`;
                container.appendChild(div);
            });
        }
        
        function apagarCaptura(index){ capturas.splice(index,1); renderCapturas(); }

        /* ================== SAÚDE DAS ABELHAS ================== */
        function registrarSaude(){
            const saude=document.getElementById("saudeInput").value.trim();
            const data=new Date();
            if(!saude){ alert("Preencha o estado de saúde"); return; }
            registrosSaude.push({saude,data});
            renderSaude();
            document.getElementById("saudeInput").value="";
            mostrarNotificacao("Registro de saúde adicionado!");
        }
        
        function renderSaude(){
            const container=document.getElementById("listaSaude");
            container.innerHTML="";
            registrosSaude.forEach((reg,index)=>{
                const div=document.createElement("div");
                div.className="registro";
                div.innerHTML=`<strong>Data/Hora:</strong> ${reg.data.toLocaleString()}<br>
                <strong>Saúde:</strong> ${reg.saude}<br>
                <button onclick="apagarSaude(${index})">Apagar</button>`;
                container.appendChild(div);
            });
        }
        
        function apagarSaude(index){ registrosSaude.splice(index,1); renderSaude(); }

        /* ================== PRODUÇÃO DE MEL ================== */
        function registrarMel(){
            const quantidade=document.getElementById("quantMel").value.trim();
            const qualidade=document.getElementById("qualidadeMel").value.trim();
            const data=new Date();
            if(!quantidade || isNaN(quantidade) || !qualidade){ alert("Preencha corretamente"); return; }
            registrosMel.push({quantidade,qualidade,data});
            renderMel();
            document.getElementById("quantMel").value="";
            document.getElementById("qualidadeMel").value="";
            mostrarNotificacao("Produção de mel registrada!");
        }
        
        function renderMel(){
            const container=document.getElementById("listaMel");
            container.innerHTML="";
            registrosMel.forEach((mel,index)=>{
                const div=document.createElement("div");
                div.className="registro";
                div.innerHTML=`<strong>Data/Hora:</strong> ${mel.data.toLocaleString()}<br>
                <strong>Quantidade:</strong> ${mel.quantidade}<br>
                <strong>Qualidade:</strong> ${mel.qualidade}<br>
                <button onclick="apagarMel(${index})">Apagar</button>`;
                container.appendChild(div);
            });
        }
        
        function apagarMel(index){ registrosMel.splice(index,1); renderMel(); }