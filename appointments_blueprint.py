from flask import Blueprint, jsonify, request, g
import psycopg2.extras

from db_helpers import get_db_connection
from auth_middleware import token_required

appointments_blueprint = Blueprint("appointments_blueprint", __name__)


# CREATE
@appointments_blueprint.route("/appointments", methods=["POST"])
@token_required
def create_appointment():
    try:
        data = request.get_json()

        user_id = g.user["id"]

        title = data["title"]
        date_time = data["date_time"]  # "YYYY-MM-DD HH:MM:SS"

        doctor_name = data.get("doctor_name")
        appointment_type = data.get("appointment_type")
        location = data.get("location")
        notes = data.get("notes")

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            INSERT INTO appointments (user_id, title, date_time, doctor_name, appointment_type, location, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (user_id, title, date_time, doctor_name, appointment_type, location, notes),
        )

        created_appointment = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify(created_appointment), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# INDEX (solo las citas del user)
@appointments_blueprint.route("/appointments", methods=["GET"])
@token_required
def appointments_index():
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
        cursor.close()
        connection.close()

        return jsonify(appointments), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# SHOW (ownership check)
@appointments_blueprint.route("/appointments/<appointment_id>", methods=["GET"])
@token_required
def show_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM appointments WHERE id = %s;", (appointment_id,))
        appointment = cursor.fetchone()

        if appointment is None:
            cursor.close()
            connection.close()
            return jsonify({"error": "Appointment not found"}), 404

        if appointment["user_id"] != g.user["id"]:
            cursor.close()
            connection.close()
            return jsonify({"error": "Forbidden"}), 403

        cursor.close()
        connection.close()

        return jsonify(appointment), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# UPDATE (ownership check)
@appointments_blueprint.route("/appointments/<appointment_id>", methods=["PUT"])
@token_required
def update_appointment(appointment_id):
    try:
        data = request.get_json()

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM appointments WHERE id = %s;", (appointment_id,))
        appointment_to_update = cursor.fetchone()

        if appointment_to_update is None:
            cursor.close()
            connection.close()
            return jsonify({"error": "Appointment not found"}), 404

        if appointment_to_update["user_id"] != g.user["id"]:
            cursor.close()
            connection.close()
            return jsonify({"error": "Forbidden"}), 403

        cursor.execute(
            """
            UPDATE appointments
            SET title = %s,
                date_time = %s,
                doctor_name = %s,
                appointment_type = %s,
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
                data.get("location"),
                data.get("notes"),
                appointment_id,
            ),
        )

        updated_appointment = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify(updated_appointment), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# DELETE (ownership check)
@appointments_blueprint.route("/appointments/<appointment_id>", methods=["DELETE"])
@token_required
def delete_appointment(appointment_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM appointments WHERE id = %s;", (appointment_id,))
        appointment_to_delete = cursor.fetchone()

        if appointment_to_delete is None:
            cursor.close()
            connection.close()
            return jsonify({"error": "Appointment not found"}), 404

        if appointment_to_delete["user_id"] != g.user["id"]:
            cursor.close()
            connection.close()
            return jsonify({"error": "Forbidden"}), 403

        cursor.execute("DELETE FROM appointments WHERE id = %s;", (appointment_id,))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify(appointment_to_delete), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
