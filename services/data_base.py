import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps
import pytz
from services import logging


log_action = logging.log_action

load_dotenv()

conn = None


def connect_db():
    """Устанавливает подключение к БД и сохраняет его в глобальной переменной."""
    global conn
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

    print("✅ Подключение к БД установлено")


def close_db():
    """Закрывает подключение к БД, если оно было установлено."""
    global conn
    if conn:
        conn.close()
        print("🛑 Подключение к БД закрыто")


def db_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with conn.cursor() as cur:
                return func(cur, *args, **kwargs)
        except psycopg2.Error as e:
            print(f"❌ Ошибка в {func.__name__}:", e)
            try:
                conn.rollback()
            except Exception:
                pass
            return None
    return wrapper


@db_operation
def get_info(cur, user_id: int) -> dict:
    # user_id
    # available_tokens
    # registration date and time
    # date when subscription expires
    # subscription type

    # запрос в БД
    if check_sub_expired(user_id):
        cancel_subscription(user_id)

    cur.execute("""
        SELECT available_tokens,
                reg_date,
                sub_expired,
                sub_type
        FROM users
        WHERE user_id = %s;
        """, (user_id,)
    )

    available_tokens, reg_date, sub_expired, sub_type = cur.fetchone()

    # #return
    return {
        "user_id": user_id,
        "available_tokens": available_tokens,
        "reg_date": reg_date,
        "sub_expired": sub_expired,
        "sub_type": sub_type,
    }


@db_operation
def reg_user(cur, user_id: int) -> None:

    if not check_user(user_id=user_id):
        log_action(user_id, "!!!Новый пользователь!!!")
        cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING;", (user_id,))
        conn.commit()

        cancel_subscription(user_id)
        print(f'{user_id}:user_regged')


@db_operation
def set_subscription(cur, user_id: int, sub_type: str, tokens: int, expired_date) -> None:
    cur.execute("""
                UPDATE users
                SET sub_type=%s,
                sub_expired=%s,
                available_tokens=%s
                WHERE user_id=%s;
                """,
                (sub_type, expired_date, tokens, user_id))
    conn.commit()


@db_operation
def cancel_subscription(cur, user_id: int) -> None:
    cur.execute("""
                UPDATE users
                SET available_tokens=%s,
                sub_type=%s,
                sub_expired=NOW() + INTERVAL '10 years'
                WHERE user_id=%s;
                """,
                (3, "free_sub", user_id))
    conn.commit()


@db_operation
def check_user(cur, user_id: int) -> bool:
    cur.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
    if cur.fetchone():
        return True
    else:
        return False


@db_operation
def get_daily_stat(cur, date: datetime.date) -> int:
    cur.execute("""
                SELECT COUNT(*)
                FROM generations
                WHERE DATE(created_at) = %s;
                """, (date,))
    gen_count = int(cur.fetchone()[0])
    cur.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM generations
                WHERE DATE(created_at) = %s;
                """, (date,))
    users_gen_count = int(cur.fetchone()[0])
    cur.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM users
                WHERE DATE(reg_date) = %s;
                """, (date,))
    newcomers_count = int(cur.fetchone()[0])
    return {
        "gen_count": gen_count,
        "users_gen_count": users_gen_count,
        "newcomers_count": newcomers_count
    }


@db_operation
def get_monthly_stat(cur, date: datetime.date) -> dict:
    year = date.year
    month = date.month
    cur.execute("""
                SELECT COUNT(*)
                FROM generations
                WHERE EXTRACT(YEAR FROM created_at) = %s
                AND EXTRACT(MONTH FROM created_at) = %s;
                """, (year, month))
    gen_count = int(cur.fetchone()[0])
    cur.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM generations
                WHERE EXTRACT(YEAR FROM created_at) = %s
                AND EXTRACT(MONTH FROM created_at) = %s;
                """, (year, month))
    users_gen_count = int(cur.fetchone()[0])
    cur.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM users
                WHERE EXTRACT(YEAR FROM reg_date) = %s
                AND EXTRACT(MONTH FROM reg_date) = %s;
                """, (year, month))
    newcomers_count = int(cur.fetchone()[0])

    return {
        "gen_count": gen_count,
        "users_gen_count": users_gen_count,
        "newcomers_count": newcomers_count
    }


@db_operation
def log_generation(cur, user_id: int, prompt: str, response: str, session_id: str) -> None:
    cur.execute("""
                INSERT INTO generations (user_id, prompt, response, created_at, session_id)
                VALUES (%s, %s, %s, NOW(), %s);""", (user_id, prompt, response, session_id))
    conn.commit()


@db_operation
def write_off_a_token(cur, user_id: int) -> None:
    user_info = get_info(user_id)
    cur.execute("UPDATE users SET available_tokens=%s WHERE user_id=%s;",
                (int(user_info["available_tokens"]) - 1, user_id,))
    conn.commit()


@db_operation
def get_prompt_by_session_id(cur, session_id: str) -> str:
    cur.execute("SELECT prompt FROM generations WHERE session_id=%s;", (session_id,))
    prompt = cur.fetchone()[0]
    return prompt


@db_operation
def set_last_request_time(cur, user_id):
    cur.execute("UPDATE users SET last_request_time=NOW() WHERE user_id=%s;", (user_id,))
    conn.commit()


@db_operation
def get_permition_by_last_request_time(cur, user_id) -> dict:
    moscow_tz = pytz.timezone("Europe/Moscow")
    five_sec_ago = datetime.now(moscow_tz) - timedelta(seconds=5)
    cur.execute("SELECT last_request_time FROM users WHERE user_id=%s;", (user_id,))
    last_request_time = cur.fetchone()

    if not last_request_time:
        return {
            "status": "allowed"
        }
    last_request_time = last_request_time[0]
    if last_request_time > five_sec_ago:
        return {
            "status": "not allowed",
            "message": "request frequency exceeded"
        }
    else:
        return {
            "status": "allowed"
        }


@db_operation
def check_sub_expired(cur, user_id: int) -> bool:
    cur.execute("SELECT sub_expired FROM users WHERE user_id=%s;", (user_id,))
    sub_expired = cur.fetchone()[0]
    moscow_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(moscow_tz)
    if sub_expired < now:
        return True
    else:
        return False


@db_operation
def get_gens_by_date_range(cur, date_start, date_end):
    cur.execute(
        """
        SELECT DATE(created_at), COUNT(*)
        FROM generations
        WHERE created_at BETWEEN %s AND %s
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
        """, (date_start, date_end))
    result = cur.fetchall()
    return result


@db_operation
def get_users_by_date_range(cur, date_start, date_end):
    cur.execute(
        """
        SELECT DATE(created_at), COUNT(DISTINCT user_id)
        FROM generations
        WHERE created_at BETWEEN %s AND %s
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
        """, (date_start, date_end))
    result = cur.fetchall()
    return result


@db_operation
def get_inactive_users(cur):
    cur.execute(
        """
        SELECT user_id
        FROM users
        WHERE last_request_time < NOW() - INTERVAL '1 day'
        """)
    data = cur.fetchall()
    return data


@db_operation
def send_mess_after_first_second_gen(cur, user_id):
    cur.execute(
        """
        SELECT sub_type
        FROM users
        WHERE user_id=%s
        """, (user_id,))
    sub_type = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM generations
        WHERE user_id=%s
        """, (user_id,))
    count = cur.fetchone()[0]

    if sub_type == 'free_sub':
        print(f"{user_id}:generations:{count}")
        if count == 1:
            return '1'
        elif count == 2:
            return '2'
        elif count == 3:
            return '3'
        else:
            return None
    else:
        return None


if __name__ == '__main__':
    connect_db()
    close_db()
