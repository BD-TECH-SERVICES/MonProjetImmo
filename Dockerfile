# Utilisation d'une image Python
FROM python:3.10

# Définition du répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Copier les fichiers de l'application
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer Tailwind CSS et ses dépendances
RUN npm install -D tailwindcss postcss autoprefixer

# Générer les fichiers de configuration
RUN npx tailwindcss init -p

# Exposer le port pour Django
EXPOSE 9000

# Commande pour démarrer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
