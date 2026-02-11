from flask import Blueprint, jsonify, request, g
import psycopg2.extras

from db_helpers import get_db_connection
from auth_middleware import token_required

appointments_blueprint = Blueprint("appointments_blueprint", __name__)

ALLOWED_STATUS = {"scheduled", "completed", "canceled"}


# CREATE
@appointments_blueprint.route("/appointments", methods=["POST"])
@token_required
def create_appointment():
    connection = None
    cursor = None
    try:
        data = request.get_json()

        user_id = g.user["id"]

        title = data["title"]
        date_time = data["date_time"]  # "YYYY-MM-DD HH:MM:SS"

        doctor_name = data.get("doctor_name")
        appointment_type = data.get("appointment_type")

        status = data.get("status", "scheduled")
        if status not in ALLOWED_STATUS:
            return jsonify({"error": "Invalid status"}), 400

        location = data.get("location")
        notes = data.get("notes")

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            INSERT INTO appointments (user_id, title, date_time, doctor_name, appointment_type, status, location, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (user_id, title, date_time, doctor_name, appointment_type, status, location, notes),
        )

        created_appointment = cursor.fetchone()
        connection.commit()

        return jsonify(created_appointment), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# INDEX (solo citas del user logueado)
@appointments_blueprint.route("/appointments", methods=["GET"])
@token_required
def appointments_index():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT *
            FROM appointments
            WHERE user_id = %s
            ORDER BY date_time ASC;
            """,
            (g.user["id"],),
        )

        appointments = cursor.fetchall()
        return jsonify(appointments), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# SHOW (ownership check)
@appointments_blueprint.route("/appointments/<appointment_id>", methods=["GET"])
@token_required
def show_appointment(appointment_id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM appointments WHERE id = %s;", (appointment_id,))
        appointment = cursor.fetchone()

        if appointment is None:
            return jsonify({"error": "Appointment not found"}), 404

        if appointment["user_id"] != g.user["id"]:
            return jsonify({"error": "Forbidden"}), 403

        return jsonify(appointment), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# UPDATE (ownership check)
@appointments_blueprint.route("/appointments/<appointment_id>", methods=["PUT"])
@token_required
def update_appointment(appointment_id):
    connection = None
    cursor = None
    try:
        data = request.get_json()

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM appointments WHERE id = %s;", (appointment_id,))
        appointment_to_update = cursor.fetchone()

        if appointment_to_update is None:
            return jsonify({"error": "Appointment not found"}), 404

        if appointment_to_update["user_id"] != g.user["id"]:
            return jsonify({"error": "Forbidden"}), 403

        status = data.get("status", appointment_to_update["status"])
        if status not in ALLOWED_STATUS:
            return jsonify({"error": "Invalid status"}), 400

        cursor.execute(
            """
            UPDATE appointments
            SET title = %s,
                date_time = %s,
                doctor_name = %s,
                appointment_type = %s,
                status = %s,
                location = %s,
                notes = %s
            WHERE id = %s
            RETURNING *;
            """,
            (
                data["title"],
                data["date_time"],
                data.get("doctor_name"),
                data.get("appointment_type"),
                status,
                data.get("location"),
                data.get("notes"),
                appointment_id,
            ),
        )

        updated_appointment = cursor.fetchone()
        connection.commit()

        return jsonify(updated_appointment), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# DELETE (ownership check)
@appointments_blueprint.route("/appointments/<appointment_id>", methods=["DELETE"])
@token_required
def delete_appointment(appointment_id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM appointments WHERE id = %s;", (appointment_id,))
        appointment_to_delete = cursor.fetchone()

        if appointment_to_delete is None:
            return jsonify({"error": "Appointment not found"}), 404

        if appointment_to_delete["user_id"] != g.user["id"]:
            return jsonify({"error": "Forbidden"}), 403

        cursor.execute("DELETE FROM appointments WHERE id = %s;", (appointment_id,))
        connection.commit()

        return jsonify(appointment_to_delete), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
