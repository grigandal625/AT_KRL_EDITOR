import argparse
import os


def get_args() -> dict:
    # Argument parser setup
    parser = argparse.ArgumentParser(
        prog="at-krl-editor", description="Editor component and server for temporal knowledge base"
    )
    parser.add_argument(
        "-u", "--url", help="RabbitMQ URL to connect", required=False, default=os.getenv("RABBIT_MQ_URL", None)
    )
    parser.add_argument(
        "-H",
        "--host",
        help="RabbitMQ host to connect",
        required=False,
        default=os.getenv("RABBIT_MQ_HOST", "localhost"),
    )
    parser.add_argument(
        "-p",
        "--port",
        help="RabbitMQ port to connect",
        required=False,
        default=int(os.getenv("RABBIT_MQ_HOST", 5672)),
        type=int,
    )
    parser.add_argument(
        "-L",
        "--login",
        "-U",
        "--user",
        "--user-name",
        "--username",
        "--user_name",
        dest="login",
        help="RabbitMQ login to connect",
        required=False,
        default=os.getenv("RABBIT_MQ_USER", "guest"),
    )
    parser.add_argument(
        "-P",
        "--password",
        help="RabbitMQ password to connect",
        required=False,
        default=os.getenv("RABBIT_MQ_PASS", "guest"),
    )
    parser.add_argument(
        "-v",
        "--virtualhost",
        "--virtual-host",
        "--virtual_host",
        dest="virtualhost",
        help="RabbitMQ virtual host to connect",
        required=False,
        default=os.getenv("RABBIT_MQ_VIRTUALHOST", "/"),
    )

    parser.add_argument(
        "-sh",
        "--server-host",
        dest="server_host",
        help="Server host",
        required=False,
        default=os.getenv("AT_KRL_EDITOR_HOST", "localhost"),
    )

    parser.add_argument(
        "-sp",
        "--server-port",
        dest="server_port",
        help="Server port",
        required=False,
        default=int(os.getenv("AT_KRL_EDITOR_PORT", 8000)),
        type=int,
    )

    # REDIS_HOST
    parser.add_argument(
        "-rh",
        "--redis-host",
        dest="redis_host",
        help="Redis host",
        required=False,
        default=os.getenv("REDIS_HOST", "localhost"),
    )

    # REDIS_PORT
    parser.add_argument(
        "-rp",
        "--redis-port",
        dest="redis_port",
        help="Redis port",
        required=False,
        default=int(os.getenv("REDIS_PORT", 6379)),
        type=int,
    )

    # REDIS_PASS
    parser.add_argument(
        "-rpass",
        "--redis-pass",
        dest="redis_pass",
        help="Redis password",
        required=False,
        default=os.getenv("REDIS_PASS", None),
    )

    # DB_ENGINE
    parser.add_argument(
        "-db",
        "--db-engine",
        dest="db_engine",
        help="Database engine",
        required=False,
        default=os.getenv("DB_ENGINE", "postgres"),
        choices=["postgres", "sqlite"],
    )

    # DB_NAME
    parser.add_argument(
        "-dbname",
        "--db-name",
        dest="db_name",
        help="Database name",
        required=False,
        default=os.getenv("DB_NAME", "at_krl_editor"),
    )

    # DB_USER
    parser.add_argument(
        "-dbuser",
        "--db-user",
        dest="db_user",
        help="Database user",
        required=False,
        default=os.getenv("DB_USER", "at_krl"),
    )

    # DB_PASSWORD
    parser.add_argument(
        "-dbpass",
        "--db-password",
        dest="db_password",
        help="Database password",
        required=False,
        default=os.getenv("DB_PASS", None),
    )

    # DB_HOST
    parser.add_argument(
        "-dbh",
        "--db-host",
        dest="db_host",
        help="Database host",
        required=False,
        default=os.getenv("DB_HOST", "localhost"),
    )

    # DB_PORT
    parser.add_argument(
        "-dbpt",
        "--db-port",
        dest="db_port",
        help="Database port",
        required=False,
        default=int(os.getenv("DB_PORT", 5432)),
        type=int,
    )

    args = parser.parse_args()
    res = vars(args)
    return res


ARGS_TO_ENV_MAPPING = {
    "url": "RABBIT_MQ_URL",
    "host": "RABBIT_MQ_HOST",
    "port": "RABBIT_MQ_PORT",
    "login": "RABBIT_MQ_USER",
    "password": "RABBIT_MQ_PASS",
    "virtualhost": "RABBIT_MQ_VIRTUALHOST",
    "server_host": "AT_KRL_EDITOR_HOST",
    "server_port": "AT_KRL_EDITOR_PORT",
    "redis_host": "REDIS_HOST",
    "redis_port": "REDIS_PORT",
    "redis_pass": "REDIS_PASS",
    "db_engine": "DB_ENGINE",
    "db_name": "DB_NAME",
    "db_user": "DB_USER",
    "db_password": "DB_PASS",
}
