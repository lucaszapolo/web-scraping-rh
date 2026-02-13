@echo off
echo ===================================================
echo   Iniciando Busca Candidato X-Ray...
echo   Acesse pelo navegador em: http://localhost:8501
echo   Para acesso na rede: http://<SEU-IP>:8501
echo ===================================================

cd /d "%~dp0"
python -m streamlit run app.py --server.address 0.0.0.0

pause
