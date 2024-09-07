@echo off
REM Configurações
SET NSSM_PATH=C:\agentSysp\nssm.exe
SET AGENT_SCRIPT_PATH=C:\agentSysp\agente.py
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

REM Remove o serviço existente (se houver)
echo Removendo serviço existente...
"%NSSM_PATH%" remove %SERVICE_NAME% confirm

REM Instala o novo serviço
echo Instalando o serviço...
"%NSSM_PATH%" install %SERVICE_NAME% python "%AGENT_SCRIPT_PATH%"

REM Configura o serviço para reiniciar automaticamente
"%NSSM_PATH%" set %SERVICE_NAME% Restart auto

REM Inicia o serviço
echo Iniciando o serviço...
"%NSSM_PATH%" start %SERVICE_NAME%

REM Exibe o status do serviço
echo Status do serviço:
"%NSSM_PATH%" status %SERVICE_NAME%

echo Instalação concluída.
pause
