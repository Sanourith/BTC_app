FROM oraclelinux:9-slim

# Création de l'utilisateur et du groupe MySQL (personnalisable : UID/GID, nom d'utilisateur)
RUN set -eux; \
    groupadd --system --gid 999 mysql; \
    useradd --system --uid 999 --gid 999 --home-dir /var/lib/mysql --no-create-home mysql

# Ajout de gosu pour faciliter l'exécution en tant qu'utilisateur non-root (optionnel)
ENV GOSU_VERSION=1.17
RUN set -eux; \
    arch="$(uname -m)"; \
    case "$arch" in \
        aarch64) gosuArch='arm64' ;; \
        x86_64) gosuArch='amd64' ;; \
        *) echo >&2 "error: unsupported architecture: '$arch'"; exit 1 ;; \
    esac; \
    curl -fL -o /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$gosuArch"; \
    chmod +x /usr/local/bin/gosu; \
    gosu --version

# Installation des dépendances système minimales (personnalisable : ajouter/supprimer des paquets)
RUN set -eux; \
    microdnf install -y \
        bzip2 gzip openssl xz zstd findutils \
    && microdnf clean all

# Ajout de la clé GPG MySQL (peut être mis à jour si la clé change)
RUN set -eux; \
    key='BCA4 3417 C3B4 85DD 128E C6D4 B7B3 B788 A8D3 785C'; \
    export GNUPGHOME="$(mktemp -d)"; \
    gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key"; \
    gpg --batch --export --armor "$key" > /etc/pki/rpm-gpg/RPM-GPG-KEY-mysql; \
    rm -rf "$GNUPGHOME"

# Configuration des dépôts MySQL (peut être modifié pour une autre version de MySQL)
ENV MYSQL_MAJOR=innovation
ENV MYSQL_VERSION=9.2.0-1.el9
RUN set -eu; \
    echo "[mysqlinnovation-server-minimal]" > /etc/yum.repos.d/mysql-community-minimal.repo; \
    echo "name=MySQL innovation Server Minimal" >> /etc/yum.repos.d/mysql-community-minimal.repo; \
    echo "baseurl=https://repo.mysql.com/yum/mysql-innovation-community/docker/el/9/\$basearch/" >> /etc/yum.repos.d/mysql-community-minimal.repo; \
    echo "gpgcheck=1" >> /etc/yum.repos.d/mysql-community-minimal.repo; \
    echo "gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-mysql" >> /etc/yum.repos.d/mysql-community-minimal.repo; \
    echo "module_hotfixes=true" >> /etc/yum.repos.d/mysql-community-minimal.repo

# Installation de MySQL Server (personnalisable : version de MySQL)
RUN set -eux; \
    microdnf install -y "mysql-community-server-minimal-$MYSQL_VERSION"; \
    microdnf clean all

# Modification de la configuration MySQL (personnalisable : fichiers de conf)
RUN set -eux; \
    sed -i 's!^socket=.*!socket=/var/run/mysqld/mysqld.sock!' /etc/my.cnf; \
    { echo '[client]'; echo 'socket=/var/run/mysqld/mysqld.sock'; } >> /etc/my.cnf; \
    mkdir -p /etc/mysql/conf.d /var/lib/mysql /var/run/mysqld; \
    chown mysql:mysql /var/lib/mysql /var/run/mysqld; \
    chmod 1777 /var/lib/mysql /var/run/mysqld; \
    mysqld --version; mysql --version

# Dépôt et installation de MySQL Shell (optionnel, si non nécessaire, commenter cette section)
ENV MYSQL_SHELL_VERSION=9.2.0-1.el9
RUN set -eux; \
    microdnf install -y "mysql-shell-$MYSQL_SHELL_VERSION"; \
    microdnf clean all; \
    mysqlsh --version

# Déclaration du volume pour MySQL
VOLUME /var/lib/mysql

# Copie des scripts d'initialisation
COPY init-scripts/ /docker-entrypoint-initdb.d/
RUN chmod -R 755 /docker-entrypoint-initdb.d

# Création d'un script d'entrée par défaut si absent
RUN echo '#!/bin/bash\n\nset -e\n\nif [ -d "/docker-entrypoint-initdb.d" ]; then\n    echo "Exécution des scripts init SQL..."\n    for f in /docker-entrypoint-initdb.d/*.sql; do\n        echo "Exécution de $f"\n        mysql < "$f"\n    done\nfi\n\nexec "$@"' > /usr/local/bin/docker-entrypoint.sh && chmod +x /usr/local/bin/docker-entrypoint.sh

# Copie du script d'entrée (personnalisable : modifier ou remplacer le script d'entrypoint)
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Exposition des ports MySQL (personnalisable : modifier ou ajouter des ports)
EXPOSE 3306 33060
CMD ["mysqld"]