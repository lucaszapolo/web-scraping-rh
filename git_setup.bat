@echo off
echo ===================================================
echo   Preparando arquivos para o GitHub...
echo ===================================================

:: Inicializa o Git se nao existir
if not exist .git (
    git init
    echo [OK] Repositorio Git iniciado.
)

:: Garante que o arquivo .gitignore existe
if not exist .gitignore (
    echo .venv/ >> .gitignore
    echo venv/ >> .gitignore
    echo __pycache__/ >> .gitignore
    echo .env >> .gitignore
    echo [OK] Arquivo .gitignore criado.
)

:: Adiciona arquivos e faz o commit
git add .
git commit -m "Upload inicial do Busca Candidato X-Ray"

echo.
echo ===================================================
echo   Tudo pronto no seu computador!
echo   Agora siga os passos:
echo   1. Crie um "New Repository" no site do GitHub.
echo   2. Copie os 3 comandos que ele mostra (git remote add...)
echo   3. Cole aqui nesta tela preta e aperte Enter.
echo ===================================================
echo.
cmd /k
