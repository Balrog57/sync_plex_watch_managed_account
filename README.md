# Synchronisation Plex : Compte Admin vers Utilisateur Géré

Ce script Python permet de synchroniser automatiquement l'état de visionnage (**Vu**) et la progression de lecture (**En cours**) d'un compte administrateur Plex (ou compte principal) vers un **Utilisateur Géré** (Managed User / Home User).

C'est l'outil idéal si vous créez un profil secondaire (par exemple pour vous-même, un enfant ou un membre de la famille) et que vous souhaitez conserver votre historique de visionnage et reprendre vos films et séries exactement là où vous les aviez laissés.

## 🚀 Fonctionnalités

*   **Synchronisation du statut "Vu"** : Si un film ou un épisode est marqué comme "Vu" sur le compte source, il le sera également sur le compte cible.
*   **Synchronisation de la progression ("En cours")** : Si un média est en pause (par exemple à 45 min), le compte cible reprendra exactement à ce moment-là.
*   **Support des Utilisateurs Gérés** : Gère l'authentification spécifique des "Home Users" (qui n'ont souvent pas de mot de passe propre mais dépendent du compte admin).
*   **Fiabilité** : Utilise l'identifiant unique (`ratingKey`) des médias pour une correspondance parfaite (nécessite que les deux comptes soient sur le même serveur).
*   **Performance** : Ne traite que les éléments "Vus" ou "En cours" du compte source pour optimiser le temps d'exécution.

## ⚠️ Prérequis

Avant d'utiliser ce script, assurez-vous d'avoir :

1.  **Python 3.x** installé sur votre machine.
2.  Un accès à votre serveur Plex (URL locale ou distante).
3.  Votre **Token d'authentification Plex (X-Plex-Token)** du compte administrateur.
    *   *Comment le trouver ?* Consultez cet article officiel : [Finding your Plex Authentication Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
4.  Le compte source et le compte cible doivent avoir accès aux **mêmes bibliothèques** sur le **même serveur** (le script utilise les IDs internes de la base de données Plex).

## 📦 Installation
 
 1.  Clonez ce dépôt ou téléchargez le fichier `sync_plex_watch_managed_account.py`.
 2.  Installez les librairies requises (`plexapi` et `PySide6`) via pip :
 
 ```bash
 pip install -r requirements.txt
 ```
 
 Ou manuellement :
 ```bash
 pip install plexapi PySide6
 ```
 
 ## ⚙️ Configuration & Utilisation
 
 1.  Lancez l'application :
 ```bash
 python sync_plex_watch_managed_account.py
 ```
 
 2.  Une interface graphique s'ouvre. Remplissez les champs :
      *   **Plex URL** : L'adresse de votre serveur (ex: `http://localhost:32400` ou `http://192.168.x.x:32400`).
      *   **Plex Token** : Le jeton de l'admin. [Comment le trouver ?](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
      *   **Compte Source** : Le nom d'utilisateur du compte qui a déjà l'historique (Admin par défaut).
      *   **Compte Cible** : Le nom de l'utilisateur géré qui doit recevoir l'historique.
 
 3.  Cliquez sur **"Sauvegarder Config"** pour mémoriser vos paramètres pour la prochaine fois.
 
 4.  Cliquez sur **"Lancer la Synchro"**.
 
 Le script va afficher la progression dans la zone de logs :
 *   Connexion au serveur.
 *   Récupération du token de l'utilisateur géré.
 *   Parcours des bibliothèques et synchronisation.
 *   Afficher dans la console les éléments mis à jour (`[VU]` ou `[EN COURS]`).

## ❓ Dépannage

*   **Erreur `Impossible de trouver ou connecter l'utilisateur`** :
    *   Vérifiez que `USER_TARGET` est écrit exactement comme dans Plex (respectez les majuscules/minuscules).
    *   Assurez-vous que cet utilisateur est bien un utilisateur géré (Managed User) rattaché au compte Admin dont vous avez fourni le token.
*   **Erreur de connexion** :
    *   Vérifiez l'URL du serveur (`PLEX_URL`).
    *   Vérifiez que le serveur est accessible depuis la machine où vous lancez le script.
    *   Vérifiez la validité de votre `PLEX_TOKEN`.
*   **Rien ne se passe ("Rien à synchroniser ici")** :
    *   Le script ignore les éléments déjà synchronisés.
    *   Vérifiez que le compte source a bien des éléments vus ou en cours dans les bibliothèques partagées avec le compte cible.

## 📄 Licence / Disclaimer

Ce script est fourni "tel quel" sans garantie. Il effectue des modifications sur l'état de lecture de vos médias (marquage comme vu / progression). Bien que testé, il est recommandé de l'utiliser en connaissance de cause.
