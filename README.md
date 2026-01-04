# Plex Sync Managed User

Ce script Python permet de synchroniser l'état de visionnage (**Vu**) et la progression de lecture (**En cours**) d'un compte administrateur Plex vers un **Utilisateur Géré** (Managed User / Home User).

C'est l'outil idéal si vous créez un profil secondaire (par exemple pour vous-même ou un membre de la famille) et que vous souhaitez conserver tout votre historique et reprendre vos épisodes exactement là où vous les aviez laissés, sans utiliser de solutions lourdes comme Trakt.

## 🚀 Fonctionnalités

* **Copie le statut "Vu" :** Si un film/épisode est vu sur le compte source, il sera marqué vu sur le compte cible.
* **Synchronise la progression :** Si un film est en pause à 45min, le compte cible reprendra à 45min.
* **Compatible Utilisateurs Gérés :** Gère l'authentification complexe des "Home Users" qui n'ont pas de mot de passe propre.
* **Léger :** Utilise l'API officielle via `plexapi`.

## 🛠 Prérequis

* Python 3.x
* Un accès à votre serveur Plex (IP + Token)

## 📦 Installation

1. Clonez ce dépôt ou téléchargez le fichier `sync_plex.py`.
2. Installez la dépendance nécessaire :

```bash
pip install plexapi

Comment trouver son Token ? > Consultez cet article : [Finding your Plex Authentication Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
