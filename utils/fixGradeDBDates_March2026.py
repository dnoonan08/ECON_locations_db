import re
import sys

sys.path.append('..')
from GradesDB import GradesDatabase

grade_db = GradesDatabase('../database_files/test_grade_database.db')

match_pattern = '.*_chip_(\d+)_(.*).json'
_file = open('clean_needCopy_44_2026-03-14_11-40-43.txt')
uploads = re.findall(match_pattern, _file.read())

for chip,timestamp in uploads[:]:
#    print(chip,timestamp)
    date,time = timestamp.split('_')
    time = time.replace('-',':')
    x = grade_db.getChip(int(chip)).time.values[-1]
#    print(x)
    grade_db.cursor.execute(f'UPDATE grades SET time="{date} {time}" WHERE chip_id={chip} and time="{x}"')
grade_db.conn.commit()
