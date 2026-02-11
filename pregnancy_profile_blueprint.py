from flask import Blueprint, jsonify, request, g
import psycopg2.extras
from db_helpers import get_db_connection
from auth_middleware import token_required

pregnancy_profile_blueprint = Blueprint("pregnancy_profile_blueprint", __name__)


@pregnancy_profile_blueprint.route("/profile", methods=["GET"])
@token_required
def get_profile():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            "SELECT * FROM pregnancy_profiles WHERE user_id = %s;",
            (g.user["id"],),
        )
        profile = cursor.fetchone()

        # ✅ si no existe, NO es error: devolvemos null
        if profile is None:
            return jsonify(None), 200

        return jsonify(profile), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@pregnancy_profile_blueprint.route("/profile", methods=["POST"])
@token_required
def create_profile():
    connection = None
    cursor = None
    try:
        data = request.get_json()
        due_date = data["due_date"]  # "YYYY-MM-DD"
        baby_nickname = data.get("baby_nickname")

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            "SELECT * FROM pregnancy_profiles WHERE user_id = %s;",
            (g.user["id"],),
        )
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "Profile already exists"}), 400

        cursor.execute(
            """
            INSERT INTO pregnancy_profiles (user_id, due_date, baby_nickname)
            VALUES (%s, %s, %s)
            RETURNING *;
            """,
            (g.user["id"], due_date, baby_nickname),
        )

        created = cursor.fetchone()
        connection.commit()
        return jsonify(created), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@pregnancy_profile_blueprint.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    connection = None
    cursor = None
    try:
        data = request.get_json()
        due_date = data["due_date"]
        baby_nickname = data.get("baby_nickname")

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            "SELECT * FROM pregnancy_profiles WHERE user_id = %s;",
            (g.user["id"],),
        )
        existing = cursor.fetchone()
        if existing is None:
            return jsonify({"error": "Profile not found"}), 404

        cursor.execute(
            """
            UPDATE pregnancy_profiles
            SET due_date = %s,
                baby_nickname = %s
            WHERE user_id = %s
            RETURNING *;
            """,
            (due_date, baby_nickname, g.user["id"]),
        )

        updated = cursor.fetchone()
        connection.commit()
        return jsonify(updated), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

