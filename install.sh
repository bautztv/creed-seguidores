#!/bin/bash
echo "🔧 Atualizando Termux e instalando dependências..."
pkg update -y
pkg upgrade -y
pkg install -y python git

echo "📥 Clonando repositório do bot..."
if [ ! -d "creed-seguidores" ]; then
  git clone https://github.com/bautztv/creed-seguidores.git
fi

cd creed-seguidores

echo "📦 Instalando dependências python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Iniciando bot..."
nohup python3 bot.py &
echo "Bot rodando em segundo plano."