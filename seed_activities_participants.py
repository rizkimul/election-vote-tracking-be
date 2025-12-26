
import sys
import os
import random
from datetime import date, timedelta
from faker import Faker
from sqlalchemy.orm import Session

# Add current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.database import SessionLocal, engine, Base
from app.models import ActivityType, Event, Attendee

# Initialize Faker with Indonesian locale
fake = Faker('id_ID')

# KECAMATAN_DATA based on src/lib/wilayah-data.ts
KECAMATAN_DATA = [
  {
    "name": 'ARJASARI',
    "dapil": 'JABAR 2-1',
    "villages": [
      { "name": 'Arjasari', "type": 'Desa' },
      { "name": 'Baros', "type": 'Desa' },
      { "name": 'Lebakwangi', "type": 'Desa' },
      { "name": 'Mekarjaya', "type": 'Desa' },
      { "name": 'Pinggirsari', "type": 'Desa' },
      { "name": 'Rancakole', "type": 'Desa' },
    ]
  },
  {
    "name": 'BALEENDAH',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Andir', "type": 'Desa' },
      { "name": 'Baleendah', "type": 'Desa' },
      { "name": 'Jelekong', "type": 'Desa' },
      { "name": 'Manggahang', "type": 'Desa' },
      { "name": 'Malakasari', "type": 'Desa' },
      { "name": 'Rancamanyar', "type": 'Desa' },
      { "name": 'Wargamekar', "type": 'Desa' },
    ]
  },
  {
    "name": 'BANJARAN',
    "dapil": 'JABAR 2-1',
    "villages": [
      { "name": 'Banjaran', "type": 'Kelurahan' },
      { "name": 'Banjaran Wetan', "type": 'Desa' },
      { "name": 'Ciapus', "type": 'Desa' },
      { "name": 'Ciherang', "type": 'Desa' },
      { "name": 'Kamasan', "type": 'Desa' },
      { "name": 'Mekarjaya', "type": 'Desa' },
      { "name": 'Neglasari', "type": 'Desa' },
      { "name": 'Pasirmulya', "type": 'Desa' },
      { "name": 'Sindangpanon', "type": 'Desa' },
      { "name": 'Tarajusari', "type": 'Desa' },
    ]
  },
  {
    "name": 'BOJONGSOANG',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Bojongsoang', "type": 'Desa' },
      { "name": 'Buahbatu', "type": 'Desa' },
      { "name": 'Cipagalo', "type": 'Desa' },
      { "name": 'Lengkong', "type": 'Desa' },
      { "name": 'Tegalluar', "type": 'Desa' },
    ]
  },
  {
    "name": 'CANGKUANG',
    "dapil": 'JABAR 2-1',
    "villages": [
      { "name": 'Bandasari', "type": 'Desa' },
      { "name": 'Ciluncat', "type": 'Desa' },
      { "name": 'Cingcin', "type": 'Desa' },
      { "name": 'Jatisari', "type": 'Desa' },
      { "name": 'Nagrak', "type": 'Desa' },
      { "name": 'Panundaan', "type": 'Desa' },
      { "name": 'Tanjungsari', "type": 'Desa' },
    ]
  },
  {
    "name": 'CICALENGKA',
    "dapil": 'JABAR 2-5',
    "villages": [
      { "name": 'Babakan Peuteuy', "type": 'Desa' },
      { "name": 'Cicalengka Kulon', "type": 'Desa' },
      { "name": 'Cicalengka Wetan', "type": 'Desa' },
      { "name": 'Cikuya', "type": 'Desa' },
      { "name": 'Dampit', "type": 'Desa' },
      { "name": 'Margaasih', "type": 'Desa' },
      { "name": 'Narawita', "type": 'Desa' },
      { "name": 'Panenjoan', "type": 'Desa' },
      { "name": 'Tanjungwangi', "type": 'Desa' },
      { "name": 'Waluya', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIKANCUNG',
    "dapil": 'JABAR 2-5',
    "villages": [
      { "name": 'Cihanyir', "type": 'Desa' },
      { "name": 'Cikancung', "type": 'Desa' },
      { "name": 'Cikasungka', "type": 'Desa' },
      { "name": 'Ciluluk', "type": 'Desa' },
      { "name": 'Hegarmanah', "type": 'Desa' },
      { "name": 'Mandalasari', "type": 'Desa' },
      { "name": 'Mekarlaksana', "type": 'Desa' },
      { "name": 'Srirahayu', "type": 'Desa' },
      { "name": 'Tanjungmekar', "type": 'Desa' },
    ]
  },
  {
    "name": 'CILENGKRANG',
    "dapil": 'JABAR 2-4',
    "villages": [
      { "name": 'Cilengkrang', "type": 'Desa' },
      { "name": 'Cipanjalu', "type": 'Desa' },
      { "name": 'Girimekar', "type": 'Desa' },
      { "name": 'Jatiendah', "type": 'Desa' },
      { "name": 'Melatiwangi', "type": 'Desa' },
    ]
  },
  {
    "name": 'CILEUNYI',
    "dapil": 'JABAR 2-4',
    "villages": [
      { "name": 'Cibiru Hilir', "type": 'Desa' },
      { "name": 'Cibiru Wetan', "type": 'Desa' },
      { "name": 'Cileunyi Kulon', "type": 'Desa' },
      { "name": 'Cileunyi Wetan', "type": 'Desa' },
      { "name": 'Cimekar', "type": 'Desa' },
      { "name": 'Cinunuk', "type": 'Kelurahan' },
    ]
  },
  {
    "name": 'CIMAUNG',
    "dapil": 'JABAR 2-1',
    "villages": [
      { "name": 'Cikalong', "type": 'Desa' },
      { "name": 'Cimaung', "type": 'Desa' },
      { "name": 'Cipinang', "type": 'Desa' },
      { "name": 'Jagabaya', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Pasirhuni', "type": 'Desa' },
      { "name": 'Sukamaju', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIMENYAN',
    "dapil": 'JABAR 2-4',
    "villages": [
      { "name": 'Cibeunying', "type": 'Desa' },
      { "name": 'Ciburial', "type": 'Desa' },
      { "name": 'Cimenyan', "type": 'Desa' },
      { "name": 'Mandalamekar', "type": 'Desa' },
      { "name": 'Mekarmanik', "type": 'Desa' },
      { "name": 'Mekarsaluyu', "type": 'Desa' },
      { "name": 'Padasuka', "type": 'Desa' },
      { "name": 'Sindangmanik', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIPARAY',
    "dapil": 'JABAR 2-3',
    "villages": [
      { "name": 'Bumiwangi', "type": 'Desa' },
      { "name": 'Ciherang', "type": 'Desa' },
      { "name": 'Cikoneng', "type": 'Desa' },
      { "name": 'Ciparay', "type": 'Kelurahan' },
      { "name": 'Gunungleutik', "type": 'Desa' },
      { "name": 'Mekarlaksana', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Pakutandang', "type": 'Desa' },
      { "name": 'Sarimahi', "type": 'Desa' },
      { "name": 'Serangmekar', "type": 'Desa' },
      { "name": 'Sumbersari', "type": 'Desa' },
      { "name": 'Tegalwaru', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIWIDEY',
    "dapil": 'JABAR 2-6',
    "villages": [
      { "name": 'Ciwidey', "type": 'Kelurahan' },
      { "name": 'Lebakmuncang', "type": 'Desa' },
      { "name": 'Nengkelan', "type": 'Desa' },
      { "name": 'Panundaan', "type": 'Desa' },
      { "name": 'Panyocokan', "type": 'Desa' },
      { "name": 'Rawabogo', "type": 'Desa' },
      { "name": 'Sukawening', "type": 'Desa' },
    ]
  },
  {
    "name": 'DAYEUHKOLOT',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Bojongemas', "type": 'Kelurahan' },
      { "name": 'Cangkuang Kulon', "type": 'Desa' },
      { "name": 'Cangkuang Wetan', "type": 'Desa' },
      { "name": 'Citeureup', "type": 'Desa' },
      { "name": 'Dayeuhkolot', "type": 'Kelurahan' },
      { "name": 'Sukaasih', "type": 'Desa' },
    ]
  },
  {
    "name": 'IBUN',
    "dapil": 'JABAR 2-3',
    "villages": [
      { "name": 'Dukuh', "type": 'Desa' },
      { "name": 'Ibun', "type": 'Desa' },
      { "name": 'Karyalaksana', "type": 'Desa' },
      { "name": 'Lampegan', "type": 'Desa' },
      { "name": 'Laksana', "type": 'Desa' },
      { "name": 'Mekarwangi', "type": 'Desa' },
      { "name": 'Neglasari', "type": 'Desa' },
      { "name": 'Pangguh', "type": 'Desa' },
      { "name": 'Sudi', "type": 'Desa' },
      { "name": 'Talun', "type": 'Desa' },
      { "name": 'Tangsimekar', "type": 'Desa' },
    ]
  },
  {
    "name": 'KATAPANG',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Cilampeni', "type": 'Desa' },
      { "name": 'Gandasari', "type": 'Desa' },
      { "name": 'Katapang', "type": 'Desa' },
      { "name": 'Pangauban', "type": 'Desa' },
      { "name": 'Parungserab', "type": 'Desa' },
      { "name": 'Sangkanhurip', "type": 'Desa' },
      { "name": 'Sukamukti', "type": 'Desa' },
    ]
  },
  {
    "name": 'KERTASARI',
    "dapil": 'JABAR 2-3',
    "villages": [
      { "name": 'Ciberem', "type": 'Desa' },
      { "name": 'Cihawuk', "type": 'Desa' },
      { "name": 'Neglawangi', "type": 'Desa' },
      { "name": 'Santosa', "type": 'Desa' },
      { "name": 'Sukapura', "type": 'Desa' },
      { "name": 'Tarumajaya', "type": 'Desa' },
    ]
  },
  {
    "name": 'KUTAWARINGIN',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Buninagara', "type": 'Desa' },
      { "name": 'Cilame', "type": 'Desa' },
      { "name": 'Gajahmekar', "type": 'Desa' },
      { "name": 'Jatisari', "type": 'Desa' },
      { "name": 'Kopo', "type": 'Desa' },
      { "name": 'Kutawaringin', "type": 'Desa' },
      { "name": 'Padasuka', "type": 'Desa' },
      { "name": 'Pameuntingan', "type": 'Desa' },
      { "name": 'Patrapan', "type": 'Desa' },
    ]
  },
  {
    "name": 'MAJALAYA',
    "dapil": 'JABAR 2-3',
    "villages": [
      { "name": 'Bojong', "type": 'Desa' },
      { "name": 'Biru', "type": 'Desa' },
      { "name": 'Majakerta', "type": 'Desa' },
      { "name": 'Majalaya', "type": 'Kelurahan' },
      { "name": 'Majasetra', "type": 'Desa' },
      { "name": 'Neglasari', "type": 'Desa' },
      { "name": 'Padaulun', "type": 'Desa' },
      { "name": 'Padamulya', "type": 'Desa' },
      { "name": 'Sukamaju', "type": 'Desa' },
      { "name": 'Sukamukti', "type": 'Desa' },
      { "name": 'Wangisagara', "type": 'Desa' },
    ]
  },
  {
    "name": 'MARGAASIH',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Lagadar', "type": 'Desa' },
      { "name": 'Margaasih', "type": 'Desa' },
      { "name": 'Mekarrahayu', "type": 'Desa' },
      { "name": 'Nanjung', "type": 'Desa' },
      { "name": 'Rahayu', "type": 'Desa' },
      { "name": 'Sayati', "type": 'Desa' },
    ]
  },
  {
    "name": 'MARGAHAYU',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Margahayu Selatan', "type": 'Kelurahan' },
      { "name": 'Margahayu Tengah', "type": 'Desa' },
      { "name": 'Sayati', "type": 'Desa' },
      { "name": 'Sukamenak', "type": 'Desa' },
      { "name": 'Sulaeman', "type": 'Desa' },
    ]
  },
  {
    "name": 'NAGREG',
    "dapil": 'JABAR 2-5',
    "villages": [
      { "name": 'Bojong', "type": 'Desa' },
      { "name": 'Ciaro', "type": 'Desa' },
      { "name": 'Ciherang', "type": 'Desa' },
      { "name": 'Mandalawangi', "type": 'Desa' },
      { "name": 'Nagrek', "type": 'Desa' },
      { "name": 'Nagreg Kendan', "type": 'Desa' },
    ]
  },
  {
    "name": 'PACET',
    "dapil": 'JABAR 2-3',
    "villages": [
      { "name": 'Cinanggela', "type": 'Desa' },
      { "name": 'Cirapuan', "type": 'Desa' },
      { "name": 'Mangunharja', "type": 'Desa' },
      { "name": 'Maruyung', "type": 'Desa' },
      { "name": 'Mekar', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Nagrak', "type": 'Desa' },
      { "name": 'Pangauban', "type": 'Desa' },
      { "name": 'Sukarame', "type": 'Desa' },
      { "name": 'Tanjungwangi', "type": 'Desa' },
    ]
  },
  {
    "name": 'PAMEUNGPEUK',
    "dapil": 'JABAR 2-2',
    "villages": [
      { "name": 'Bojongkunci', "type": 'Desa' },
      { "name": 'Langonsari', "type": 'Desa' },
      { "name": 'Pameungpeuk', "type": 'Desa' },
      { "name": 'Rancatungku', "type": 'Desa' },
    ]
  },
  {
    "name": 'PANGALENGAN',
    "dapil": 'JABAR 2-6',
    "villages": [
      { "name": 'Lamajang', "type": 'Desa' },
      { "name": 'Margamukti', "type": 'Desa' },
      { "name": 'Margamekar', "type": 'Desa' },
      { "name": 'Margamulya', "type": 'Desa' },
      { "name": 'Pangalengan', "type": 'Kelurahan' },
      { "name": 'Pulosari', "type": 'Desa' },
      { "name": 'Sukaluyu', "type": 'Desa' },
      { "name": 'Sukamanah', "type": 'Desa' },
      { "name": 'Tribaktimulya', "type": 'Desa' },
      { "name": 'Wanasuka', "type": 'Desa' },
      { "name": 'Warnasari', "type": 'Desa' },
    ]
  },
  {
    "name": 'PASEH',
    "dapil": 'JABAR 2-3',
    "villages": [
      { "name": 'Cipaku', "type": 'Desa' },
      { "name": 'Ciramea', "type": 'Desa' },
      { "name": 'Karangtunggal', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Paseh', "type": 'Desa' },
      { "name": 'Sindangsari Al Hidayah', "type": 'Desa' },
      { "name": 'Sukamanah', "type": 'Desa' },
      { "name": 'Tangsungsari', "type": 'Desa' },
    ]
  },
  {
    "name": 'PASIRJAMBU',
    "dapil": 'JABAR 2-6',
    "villages": [
      { "name": 'Cibodas', "type": 'Desa' },
      { "name": 'Cukanggenteng', "type": 'Desa' },
      { "name": 'Mekarmaju', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Pasirjambu', "type": 'Desa' },
      { "name": 'Sugihmukti', "type": 'Desa' },
      { "name": 'Tenjolaya', "type": 'Desa' },
    ]
  },
  {
    "name": 'RANCABALI',
    "dapil": 'JABAR 2-6',
    "villages": [
      { "name": 'Alamendah', "type": 'Desa' },
      { "name": 'Cipelah', "type": 'Desa' },
      { "name": 'Indragiri', "type": 'Desa' },
      { "name": 'Patengan', "type": 'Desa' },
      { "name": 'Sukaresmi', "type": 'Desa' },
    ]
  },
  {
    "name": 'RANCAEKEK',
    "dapil": 'JABAR 2-4',
    "villages": [
      { "name": 'Bojongloa', "type": 'Desa' },
      { "name": 'Bojongsalam', "type": 'Desa' },
      { "name": 'Jelegong', "type": 'Desa' },
      { "name": 'Linggar', "type": 'Desa' },
      { "name": 'Nanjungmekar', "type": 'Desa' },
      { "name": 'Rancaekek Kencana', "type": 'Desa' },
      { "name": 'Rancaekek Kulon', "type": 'Desa' },
      { "name": 'Rancaekek Wetan', "type": 'Desa' },
      { "name": 'Sangiang', "type": 'Desa' },
      { "name": 'Sukadana', "type": 'Desa' },
      { "name": 'Sukamanah', "type": 'Desa' },
      { "name": 'Tegalsumedang', "type": 'Desa' },
    ]
  },
  {
    "name": 'SOLOKANJERUK',
    "dapil": 'JABAR 2-3',
    "villages": [
      { "name": 'Bojongemas', "type": 'Desa' },
      { "name": 'Cibodas', "type": 'Desa' },
      { "name": 'Langensari', "type": 'Desa' },
      { "name": 'Padamulya', "type": 'Desa' },
      { "name": 'Panyadap', "type": 'Desa' },
      { "name": 'Rancakasumba', "type": 'Desa' },
      { "name": 'Solokanjeruk', "type": 'Desa' },
      { "name": 'Sukamulya', "type": 'Desa' },
    ]
  },
  {
    "name": 'SOREANG',
    "dapil": 'JABAR 2-1',
    "villages": [
      { "name": 'Cingcin', "type": 'Desa' },
      { "name": 'Karamatmulya', "type": 'Desa' },
      { "name": 'Parungserab', "type": 'Desa' },
      { "name": 'Panyirapan', "type": 'Desa' },
      { "name": 'Pamekaran', "type": 'Desa' },
      { "name": 'Soreang', "type": 'Kelurahan' },
      { "name": 'Sukajadi', "type": 'Desa' },
      { "name": 'Sukasari', "type": 'Desa' },
      { "name": 'Sukanagara', "type": 'Desa' },
    ]
  }
]

def seed_data():
    db = SessionLocal()
    try:
        print("Starting seed process...")
        
        # 1. Get ALL existing ActivityTypes from the database
        all_activity_types = db.query(ActivityType).all()
        
        if not all_activity_types:
            print("No Activity Types found in the database. Please create some first.")
            return
        
        print(f"Found {len(all_activity_types)} Activity Types:")
        for at in all_activity_types:
            print(f"  - {at.id}: {at.name}")

        # 2. Iterate through Kecamatan
        total_activities = 0
        total_attendees = 0
        activity_type_index = 0  # To rotate through activity types
        
        for kec in KECAMATAN_DATA:
            kec_name = kec['name']
            dapil = kec['dapil']
            villages = kec['villages']
            
            print(f"Processing Kecamatan: {kec_name}")
            
            # Create 2 Activities per Kecamatan, using different activity types
            for i in range(2):
                # Round-robin through all activity types
                activity_type = all_activity_types[activity_type_index % len(all_activity_types)]
                activity_type_index += 1
                
                # Randomly select a village for the event location
                village_obj = random.choice(villages)
                village_name = village_obj['name']
                
                # Random date within last 6 months to next month
                event_date = fake.date_between(start_date='-6m', end_date='+1m')
                
                # Create Event
                event = Event(
                    activity_type_id=activity_type.id,
                    dapil=dapil,
                    kecamatan=kec_name,
                    desa=village_name,
                    # JSON structure for hierarchy if needed
                    location_hierarchy={
                        "kabupaten": "KABUPATEN BANDUNG",
                        "kecamatan": kec_name,
                        "desa": village_name
                    },
                    date=event_date,
                    target_participants=50
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                total_activities += 1
                
                # 3. Create 10 Participants per Event
                # Correlated Data: Participants are from the same Kecamatan
                # Mix of same village and other villages in the same kec
                
                attendees_to_add = []
                for _ in range(10):
                    # 70% chance from same village, 30% from neighbor village in same kec
                    if random.random() < 0.7:
                        p_village_name = village_name
                    else:
                        p_village_name = random.choice(villages)['name']
                    
                    gender = random.choice(['L', 'P'])
                    age = random.randint(17, 85)
                    
                    # Generate a fake but realistic NIK (16 digits)
                    # 32 (Jabar) 04 (Bandung)
                    nik_prefix = "3204"
                    nik_rest = fake.numerify(text='############')
                    nik = nik_prefix + nik_rest
                    
                    attendee = Attendee(
                        event_id=event.id,
                        nik=nik,
                        identifier_type="NIK",
                        name=fake.name_male() if gender == 'L' else fake.name_female(),
                        kecamatan=kec_name, # Correlated: Same kecamatan
                        desa=p_village_name,
                        alamat=fake.address().replace('\n', ', '), # Single line address
                        jenis_kelamin=gender,
                        pekerjaan=fake.job(),
                        usia=age
                    )
                    attendees_to_add.append(attendee)
                
                # Add all attendees for this event
                db.add_all(attendees_to_add)
                try:
                    db.commit()
                    total_attendees += 10
                except Exception as e:
                    print(f"  Error adding attendees for event {event.id}: {e}")
                    db.rollback()
        
        print(f"\nSeeding Complete!")
        print(f"Total Activities Created: {total_activities}")
        print(f"Total Participants Created: {total_attendees}")
        
        # Print summary per activity type
        print("\n=== Events per Activity Type ===")
        for at in all_activity_types:
            count = db.query(Event).filter(Event.activity_type_id == at.id).count()
            print(f"  {at.name}: {count} events")

    except Exception as e:
        print(f"Critical Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

