@echo off
echo ==========================================================
echo   Configurando Firewall para Busca Candidato (Porta 8501)
echo   ATENCAO: Execute este arquivo como ADMINISTRADOR!
echo ==========================================================

netsh advfirewall firewall add rule name="Streamlit BuscaCandidato" dir=in action=allow protocol=TCP localport=8501

if %errorlevel% equ 0 (
    echo.
    echo [SUCESSO] Regra de firewall criada! O sistema esta liberado na rede.
) else (
    echo.
    echo [ERRO] Falha ao criar regra. Verifique se rodou como Administrador.
)

pause
