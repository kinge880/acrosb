@echo off
REM Configurações
SET NSSM_PATH=C:\agentSysp\nssm.exe
SET AGENT_SCRIPT_PATH=C:\agentSysp\main\main.exe
SET SERVICE_NAME=AgentSysp

REM Verifica se o NSSM está disponível
IF NOT EXIST "%NSSM_PATH%" (
    echo NSSM não encontrado em %NSSM_PATH%.
    echo Baixe e extraia o NSSM antes de executar este script.
    exit /b 1
)

REM Verifica se o script do agente existe
IF NOT EXIST "%AGENT_SCRIPT_PATH%" (
    echo Script do agente não encontrado em %AGENT_SCRIPT_PATH%.
    exit /b 1
)

REM Solicita execução como administrador se necessário
echo Verificando permissões administrativas...
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo O script precisa ser executado como administrador.
    echo Feche esta janela e execute o script novamente como administrador.
    pause
    exit /b 1
)

REM Remove o serviço existente (se houver)
echo Removendo serviço existente...
"%NSSM_PATH%" remove %SERVICE_NAME% confirm

REM Pausa para garantir que o serviço seja removido corretamente
timeout /t 5 /nobreak >nul

REM Verifica se o serviço foi removido corretamente
sc query %SERVICE_NAME% | findstr /I /C:"FAILED" >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo O serviço %SERVICE_NAME% ainda existe. Reinicie o sistema e tente novamente.
    pause
    exit /b 1
)

REM Instala o novo serviço usando o executável correto
echo Instalando o serviço...
"%NSSM_PATH%" install %SERVICE_NAME% "%AGENT_SCRIPT_PATH%"

REM Configura o serviço para reiniciar automaticamente
echo Configurando o serviço para reiniciar automaticamente...
"%NSSM_PATH%" set %SERVICE_NAME% AppRestartDelay 5000

REM Inicia o serviço
echo Iniciando o serviço...
"%NSSM_PATH%" start %SERVICE_NAME%

REM Exibe o status do serviço
echo Status do serviço:
"%NSSM_PATH%" status %SERVICE_NAME%

echo Instalação concluída.
pause
