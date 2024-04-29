import sqlite3


def main():
    db = sqlite3.connect("database.db")

    db.execute('''
            CREATE TABLE IF NOT EXISTS "powermeter"
                ("timestamp" TEXT PRIMARY KEY, "power" REAL, "instant_power" REAL, "cadence" REAL)
            ''')
    
    db.execute('''
               CREATE TABLE IF NOT EXISTS "hall"
                ("timestamp" TEXT PRIMARY KEY, "hall_cadence" REAL, "speed" REAL, "distance" REAL)
            ''')

    db.execute('''
            CREATE TABLE IF NOT EXISTS "heartrate"
            ("timestamp" TEXT PRIMARY KEY, "heartrate" REAL)
            ''')

    db.execute('''
            CREATE TABLE IF NOT EXISTS "accelerometer" ( "timestamp" DATETIME, "acc_x" REAL, "acc_y" REAL, "acc_z" REAL, "gyr_x" REAL, "gyr_y" REAL, "gyr_z" REAL )
            ''')

    db.commit()


if __name__ == "__main__":
    main()