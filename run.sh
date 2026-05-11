#!/bin/bash
echo "Démarrage du bot Highrise..."
while true; do
    python3 bot.py
    echo "Bot arrêté. Redémarrage dans 5 secondes..."
    sleep 5
done
