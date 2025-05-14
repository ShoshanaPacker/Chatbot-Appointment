from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields

# from logic import  get_appointments_by_user_id, delete_appointment
from logic import post, update_appointment, get_all_appointments, get, get_appointments_by_user_id, \
    delete_appointment  # ודא שזה מיובא

from config import service, CALENDAR_ID

app = Flask(__name__)
CORS(app)  # פתרון לבעיית CORS

api = Api(app, version='1.0', title='Appointment Scheduler API',
          description='API לקביעת תורים לרופאים', doc='/')

appointment_model = api.model('Appointment', {
    'user_id': fields.String(required=True, description='ת"ז או מזהה משתמש'),
    'phon': fields.String(required=True, description='טלפון 05xxxxxxxx'),
    'date': fields.String(required=True, description='תאריך התור בפורמט YYYY-MM-DD, למשל: 2025-05-15'),
    'start_time': fields.String(required=True, description='שעת התחלה בפורמט HH:MM, למשל: 14:00'),
    'duration': fields.Integer(required=False, description='משך הפגישה בדקות', default=30),
    'Country-City': fields.String(required=False, description='אזור זמן (למשל: Asia/Jerusalem)', default='UTC'),
    'email': fields.String(required=True, description='כתובת דוא"ל (למשל: example@gmail.com)')


})


@api.route('/appointments')
class AppointmentResource(Resource):
    @api.doc('create_appointment')
    @api.expect(appointment_model)
    def post(self):
        data = api.payload
        return post(data)


@api.route('/events')
class EventList(Resource):
    @api.doc('list_events')
    def get(self):
        return get(service, CALENDAR_ID)


@api.route('/appointments/user/<string:user_id>')
@api.param('user_id', 'תעודת זהות של המשתמש')
class AppointmentByUser(Resource):
    @api.doc('get_appointments_by_user_id')
    def get(self, user_id):
        """קבלת כל התורים של משתמש לפי ת"ז"""
        return get_appointments_by_user_id(user_id, service, CALENDAR_ID)


@api.route('/appointments/<string:event_id>')
class AppointmentModifyResource(Resource):
    @api.doc('update_appointment')
    @api.expect(appointment_model)
    def put(self, event_id):
        data = api.payload
        return update_appointment(event_id, data, service, CALENDAR_ID)


@api.route('/<string:event_id>')
class AppointmentModifyResource(Resource):
    @api.doc('delete_appointment')
    def delete(self, event_id):
        return delete_appointment(event_id, service, CALENDAR_ID)



@api.route('/appointments/all')
class AllAppointments(Resource):
    def get(self):
        """קבלת כל התורים במסד הנתונים"""
        return get_all_appointments()



if __name__ == '__main__':
    app.run(debug=True)
