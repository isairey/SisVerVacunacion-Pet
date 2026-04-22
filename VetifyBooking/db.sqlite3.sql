BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "auth_group" (
	"id"	integer NOT NULL,
	"name"	varchar(150) NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
	"id"	integer NOT NULL,
	"group_id"	integer NOT NULL,
	"permission_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("permission_id") REFERENCES "auth_permission"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_permission" (
	"id"	integer NOT NULL,
	"content_type_id"	integer NOT NULL,
	"codename"	varchar(100) NOT NULL,
	"name"	varchar(255) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("content_type_id") REFERENCES "django_content_type"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_user" (
	"id"	integer NOT NULL,
	"password"	varchar(128) NOT NULL,
	"last_login"	datetime,
	"is_superuser"	bool NOT NULL,
	"username"	varchar(150) NOT NULL UNIQUE,
	"last_name"	varchar(150) NOT NULL,
	"email"	varchar(254) NOT NULL,
	"is_staff"	bool NOT NULL,
	"is_active"	bool NOT NULL,
	"date_joined"	datetime NOT NULL,
	"first_name"	varchar(150) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "auth_user_groups" (
	"id"	integer NOT NULL,
	"user_id"	integer NOT NULL,
	"group_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" (
	"id"	integer NOT NULL,
	"user_id"	integer NOT NULL,
	"permission_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("permission_id") REFERENCES "auth_permission"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "booking_appointment" (
	"id"	integer NOT NULL,
	"date"	date NOT NULL,
	"time"	time NOT NULL,
	"notes"	text NOT NULL,
	"created_at"	datetime NOT NULL,
	"user_id"	integer NOT NULL,
	"pet_id"	bigint NOT NULL,
	"status"	varchar(20) NOT NULL,
	"service"	varchar(100) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("pet_id") REFERENCES "booking_pet"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "booking_clinicschedule" (
	"id"	integer NOT NULL,
	"day_of_week"	varchar(10) NOT NULL UNIQUE,
	"is_open"	bool NOT NULL,
	"opening_time"	time NOT NULL,
	"closing_time"	time NOT NULL,
	"notes"	text NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "booking_document" (
	"id"	integer NOT NULL,
	"title"	varchar(200) NOT NULL,
	"description"	text NOT NULL,
	"category"	varchar(50) NOT NULL,
	"file"	varchar(100) NOT NULL,
	"icon"	varchar(10) NOT NULL,
	"created_at"	datetime NOT NULL,
	"is_active"	bool NOT NULL,
	"uploaded_by_id"	integer,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("uploaded_by_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "booking_pet" (
	"id"	integer NOT NULL,
	"name"	varchar(100) NOT NULL,
	"pet_type"	varchar(10) NOT NULL,
	"other_type"	varchar(50),
	"breed"	varchar(100) NOT NULL,
	"color"	varchar(50) NOT NULL,
	"age"	integer NOT NULL,
	"weight"	decimal NOT NULL,
	"vaccination_status"	varchar(10) NOT NULL,
	"allergies"	text NOT NULL,
	"friendly_with_people"	bool NOT NULL,
	"friendly_with_animals"	bool NOT NULL,
	"nervous_at_vet"	bool NOT NULL,
	"special_care"	bool NOT NULL,
	"emergency_contact_name"	varchar(200) NOT NULL,
	"emergency_contact_phone"	varchar(20) NOT NULL,
	"photo"	varchar(100),
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"owner_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("owner_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "booking_service" (
	"id"	integer NOT NULL,
	"name"	varchar(100) NOT NULL,
	"description"	text NOT NULL,
	"duration"	integer NOT NULL,
	"price"	decimal NOT NULL,
	"icon"	varchar(10) NOT NULL,
	"is_active"	bool NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "booking_userprofile" (
	"id"	integer NOT NULL,
	"avatar"	varchar(100),
	"phone"	varchar(20),
	"address"	varchar(255),
	"date_of_birth"	date,
	"bio"	text,
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"user_id"	integer NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "booking_veterinarian" (
	"id"	integer NOT NULL,
	"name"	varchar(200) NOT NULL,
	"specialty"	varchar(20) NOT NULL,
	"license_number"	varchar(50) NOT NULL,
	"email"	varchar(254) NOT NULL,
	"phone"	varchar(20) NOT NULL,
	"years_experience"	integer NOT NULL,
	"bio"	text NOT NULL,
	"available_days"	text NOT NULL CHECK((JSON_VALID("available_days") OR "available_days" IS NULL)),
	"start_time"	time NOT NULL,
	"end_time"	time NOT NULL,
	"photo"	varchar(100),
	"is_active"	bool NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_admin_log" (
	"id"	integer NOT NULL,
	"object_id"	text,
	"object_repr"	varchar(200) NOT NULL,
	"action_flag"	smallint unsigned NOT NULL CHECK("action_flag" >= 0),
	"change_message"	text NOT NULL,
	"content_type_id"	integer,
	"user_id"	integer NOT NULL,
	"action_time"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("content_type_id") REFERENCES "django_content_type"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "django_content_type" (
	"id"	integer NOT NULL,
	"app_label"	varchar(100) NOT NULL,
	"model"	varchar(100) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_migrations" (
	"id"	integer NOT NULL,
	"app"	varchar(255) NOT NULL,
	"name"	varchar(255) NOT NULL,
	"applied"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_session" (
	"session_key"	varchar(40) NOT NULL,
	"session_data"	text NOT NULL,
	"expire_date"	datetime NOT NULL,
	PRIMARY KEY("session_key")
);
INSERT INTO "auth_permission" VALUES (1,1,'add_logentry','Can add log entry');
INSERT INTO "auth_permission" VALUES (2,1,'change_logentry','Can change log entry');
INSERT INTO "auth_permission" VALUES (3,1,'delete_logentry','Can delete log entry');
INSERT INTO "auth_permission" VALUES (4,1,'view_logentry','Can view log entry');
INSERT INTO "auth_permission" VALUES (5,2,'add_permission','Can add permission');
INSERT INTO "auth_permission" VALUES (6,2,'change_permission','Can change permission');
INSERT INTO "auth_permission" VALUES (7,2,'delete_permission','Can delete permission');
INSERT INTO "auth_permission" VALUES (8,2,'view_permission','Can view permission');
INSERT INTO "auth_permission" VALUES (9,3,'add_group','Can add group');
INSERT INTO "auth_permission" VALUES (10,3,'change_group','Can change group');
INSERT INTO "auth_permission" VALUES (11,3,'delete_group','Can delete group');
INSERT INTO "auth_permission" VALUES (12,3,'view_group','Can view group');
INSERT INTO "auth_permission" VALUES (13,4,'add_user','Can add user');
INSERT INTO "auth_permission" VALUES (14,4,'change_user','Can change user');
INSERT INTO "auth_permission" VALUES (15,4,'delete_user','Can delete user');
INSERT INTO "auth_permission" VALUES (16,4,'view_user','Can view user');
INSERT INTO "auth_permission" VALUES (17,5,'add_contenttype','Can add content type');
INSERT INTO "auth_permission" VALUES (18,5,'change_contenttype','Can change content type');
INSERT INTO "auth_permission" VALUES (19,5,'delete_contenttype','Can delete content type');
INSERT INTO "auth_permission" VALUES (20,5,'view_contenttype','Can view content type');
INSERT INTO "auth_permission" VALUES (21,6,'add_session','Can add session');
INSERT INTO "auth_permission" VALUES (22,6,'change_session','Can change session');
INSERT INTO "auth_permission" VALUES (23,6,'delete_session','Can delete session');
INSERT INTO "auth_permission" VALUES (24,6,'view_session','Can view session');
INSERT INTO "auth_permission" VALUES (25,7,'add_clinicschedule','Can add Horario de Clínica');
INSERT INTO "auth_permission" VALUES (26,7,'change_clinicschedule','Can change Horario de Clínica');
INSERT INTO "auth_permission" VALUES (27,7,'delete_clinicschedule','Can delete Horario de Clínica');
INSERT INTO "auth_permission" VALUES (28,7,'view_clinicschedule','Can view Horario de Clínica');
INSERT INTO "auth_permission" VALUES (29,8,'add_service','Can add Servicio');
INSERT INTO "auth_permission" VALUES (30,8,'change_service','Can change Servicio');
INSERT INTO "auth_permission" VALUES (31,8,'delete_service','Can delete Servicio');
INSERT INTO "auth_permission" VALUES (32,8,'view_service','Can view Servicio');
INSERT INTO "auth_permission" VALUES (33,9,'add_veterinarian','Can add Veterinario');
INSERT INTO "auth_permission" VALUES (34,9,'change_veterinarian','Can change Veterinario');
INSERT INTO "auth_permission" VALUES (35,9,'delete_veterinarian','Can delete Veterinario');
INSERT INTO "auth_permission" VALUES (36,9,'view_veterinarian','Can view Veterinario');
INSERT INTO "auth_permission" VALUES (37,10,'add_document','Can add Documento');
INSERT INTO "auth_permission" VALUES (38,10,'change_document','Can change Documento');
INSERT INTO "auth_permission" VALUES (39,10,'delete_document','Can delete Documento');
INSERT INTO "auth_permission" VALUES (40,10,'view_document','Can view Documento');
INSERT INTO "auth_permission" VALUES (41,11,'add_pet','Can add Mascota');
INSERT INTO "auth_permission" VALUES (42,11,'change_pet','Can change Mascota');
INSERT INTO "auth_permission" VALUES (43,11,'delete_pet','Can delete Mascota');
INSERT INTO "auth_permission" VALUES (44,11,'view_pet','Can view Mascota');
INSERT INTO "auth_permission" VALUES (45,12,'add_appointment','Can add appointment');
INSERT INTO "auth_permission" VALUES (46,12,'change_appointment','Can change appointment');
INSERT INTO "auth_permission" VALUES (47,12,'delete_appointment','Can delete appointment');
INSERT INTO "auth_permission" VALUES (48,12,'view_appointment','Can view appointment');
INSERT INTO "auth_permission" VALUES (49,13,'add_profile','Can add profile');
INSERT INTO "auth_permission" VALUES (50,13,'change_profile','Can change profile');
INSERT INTO "auth_permission" VALUES (51,13,'delete_profile','Can delete profile');
INSERT INTO "auth_permission" VALUES (52,13,'view_profile','Can view profile');
INSERT INTO "auth_permission" VALUES (53,14,'add_userprofile','Can add user profile');
INSERT INTO "auth_permission" VALUES (54,14,'change_userprofile','Can change user profile');
INSERT INTO "auth_permission" VALUES (55,14,'delete_userprofile','Can delete user profile');
INSERT INTO "auth_permission" VALUES (56,14,'view_userprofile','Can view user profile');
INSERT INTO "auth_user" VALUES (1,'pbkdf2_sha256$1000000$K8Vm9NlvAJO4M1sj1FALWC$D0it7YFQ2qdOMVw9OCpd/mZ9vuo07zUFvI3Ug0LHeQM=','2026-03-09 02:42:01.014164',0,'Fabian','','fabiansaizgonzalez@gmail.com',0,1,'2026-03-05 01:36:43.162912','');
INSERT INTO "auth_user" VALUES (2,'pbkdf2_sha256$1000000$P4kJBR7TDW1Oz8TS1ej7hm$RbFlvq3/QOVLuxjDlz/6137ziu78nlfle+h9hnMZ79I=','2026-03-10 14:35:56.203184',1,'Fabian2','','',1,1,'2026-03-05 01:38:43.692655','');
INSERT INTO "booking_appointment" VALUES (1,'2026-03-11','12:00:00','','2026-03-09 21:21:34.416053',2,2,'pending','checkup');
INSERT INTO "booking_appointment" VALUES (2,'2026-03-26','14:00:00','','2026-03-09 22:15:32.565727',2,1,'pending','grooming');
INSERT INTO "booking_appointment" VALUES (3,'2026-03-26','12:00:00','asdfioajefi','2026-03-09 22:54:50.952466',2,1,'pending','vaccination');
INSERT INTO "booking_pet" VALUES (1,'Lorax','dog','','french poodle','blanco',9,15,'pending','',0,0,1,0,'Carolina Saiz','6645734353','','2026-03-09 20:50:36.146832','2026-03-09 20:50:36.146832',2);
INSERT INTO "booking_pet" VALUES (2,'Aslan2','cat','','siames','cafe',2,8,'updated','',1,0,1,0,'Carolina Saiz','6645734353','','2026-03-09 21:21:22.807504','2026-03-09 22:55:07.954228',2);
INSERT INTO "booking_userprofile" VALUES (1,'','','',NULL,'','2026-03-05 20:44:28.694057','2026-03-10 14:35:56.203184',2);
INSERT INTO "django_content_type" VALUES (1,'admin','logentry');
INSERT INTO "django_content_type" VALUES (2,'auth','permission');
INSERT INTO "django_content_type" VALUES (3,'auth','group');
INSERT INTO "django_content_type" VALUES (4,'auth','user');
INSERT INTO "django_content_type" VALUES (5,'contenttypes','contenttype');
INSERT INTO "django_content_type" VALUES (6,'sessions','session');
INSERT INTO "django_content_type" VALUES (7,'booking','clinicschedule');
INSERT INTO "django_content_type" VALUES (8,'booking','service');
INSERT INTO "django_content_type" VALUES (9,'booking','veterinarian');
INSERT INTO "django_content_type" VALUES (10,'booking','document');
INSERT INTO "django_content_type" VALUES (11,'booking','pet');
INSERT INTO "django_content_type" VALUES (12,'booking','appointment');
INSERT INTO "django_content_type" VALUES (13,'booking','profile');
INSERT INTO "django_content_type" VALUES (14,'booking','userprofile');
INSERT INTO "django_migrations" VALUES (1,'contenttypes','0001_initial','2026-03-05 01:35:30.091815');
INSERT INTO "django_migrations" VALUES (2,'auth','0001_initial','2026-03-05 01:35:30.132758');
INSERT INTO "django_migrations" VALUES (3,'admin','0001_initial','2026-03-05 01:35:30.173200');
INSERT INTO "django_migrations" VALUES (4,'admin','0002_logentry_remove_auto_add','2026-03-05 01:35:30.209536');
INSERT INTO "django_migrations" VALUES (5,'admin','0003_logentry_add_action_flag_choices','2026-03-05 01:35:30.246725');
INSERT INTO "django_migrations" VALUES (6,'contenttypes','0002_remove_content_type_name','2026-03-05 01:35:30.328360');
INSERT INTO "django_migrations" VALUES (7,'auth','0002_alter_permission_name_max_length','2026-03-05 01:35:30.352937');
INSERT INTO "django_migrations" VALUES (8,'auth','0003_alter_user_email_max_length','2026-03-05 01:35:30.382042');
INSERT INTO "django_migrations" VALUES (9,'auth','0004_alter_user_username_opts','2026-03-05 01:35:30.407689');
INSERT INTO "django_migrations" VALUES (10,'auth','0005_alter_user_last_login_null','2026-03-05 01:35:30.451370');
INSERT INTO "django_migrations" VALUES (11,'auth','0006_require_contenttypes_0002','2026-03-05 01:35:30.463421');
INSERT INTO "django_migrations" VALUES (12,'auth','0007_alter_validators_add_error_messages','2026-03-05 01:35:30.490993');
INSERT INTO "django_migrations" VALUES (13,'auth','0008_alter_user_username_max_length','2026-03-05 01:35:30.518837');
INSERT INTO "django_migrations" VALUES (14,'auth','0009_alter_user_last_name_max_length','2026-03-05 01:35:30.545115');
INSERT INTO "django_migrations" VALUES (15,'auth','0010_alter_group_name_max_length','2026-03-05 01:35:30.591029');
INSERT INTO "django_migrations" VALUES (16,'auth','0011_update_proxy_permissions','2026-03-05 01:35:30.610013');
INSERT INTO "django_migrations" VALUES (17,'auth','0012_alter_user_first_name_max_length','2026-03-05 01:35:30.650268');
INSERT INTO "django_migrations" VALUES (18,'booking','0001_initial','2026-03-05 01:35:30.795979');
INSERT INTO "django_migrations" VALUES (19,'sessions','0001_initial','2026-03-05 01:35:30.813357');
INSERT INTO "django_migrations" VALUES (20,'booking','0002_userprofile_delete_profile','2026-03-05 20:35:57.326061');
INSERT INTO "django_migrations" VALUES (21,'booking','0003_alter_appointment_options_appointment_status_and_more','2026-03-06 19:08:40.278257');
INSERT INTO "django_session" VALUES ('ucwrkmduv1eh761qkk5h52zdxn8z4liv','.eJxVjMsOwiAQRf-FtSGAPF267zeQgWGkaiAp7cr479qkC93ec859sQjbWuM2yhJnZBem2Ol3S5Afpe0A79Bunefe1mVOfFf4QQefOpbn9XD_DiqM-q0BJXoDltAEsDooAi_RkspBKqPOOpeAJIzXAkO21jmhyDoMRAaETuz9AewaN-k:1vzyBg:phgPtTlE3_EVCtjp7HE-Ev7vrTvyac6dns4YDmjlZcM','2026-03-24 14:35:56.218867');
CREATE INDEX IF NOT EXISTS "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" (
	"group_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" (
	"group_id",
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" (
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_permission_content_type_id_2f476e4b" ON "auth_permission" (
	"content_type_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" (
	"content_type_id",
	"codename"
);
CREATE INDEX IF NOT EXISTS "auth_user_groups_group_id_97559544" ON "auth_user_groups" (
	"group_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" (
	"user_id",
	"group_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" (
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" (
	"user_id",
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "booking_appointment_pet_id_98a85037" ON "booking_appointment" (
	"pet_id"
);
CREATE INDEX IF NOT EXISTS "booking_appointment_user_id_b2c5d5e3" ON "booking_appointment" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "booking_document_uploaded_by_id_e7c815f1" ON "booking_document" (
	"uploaded_by_id"
);
CREATE INDEX IF NOT EXISTS "booking_pet_owner_id_be8e3dff" ON "booking_pet" (
	"owner_id"
);
CREATE INDEX IF NOT EXISTS "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" (
	"content_type_id"
);
CREATE INDEX IF NOT EXISTS "django_admin_log_user_id_c564eba6" ON "django_admin_log" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" (
	"app_label",
	"model"
);
CREATE INDEX IF NOT EXISTS "django_session_expire_date_a5c62663" ON "django_session" (
	"expire_date"
);
COMMIT;
