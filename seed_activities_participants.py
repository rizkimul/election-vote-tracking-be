
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
    "dapil": 'DAPIL 7',
    "villages": [
      { "name": 'Ancolmekar', "type": 'Desa' },
      { "name": 'Arjasari', "type": 'Desa' },
      { "name": 'Baros', "type": 'Desa' },
      { "name": 'Batukarut', "type": 'Desa' },
      { "name": 'Lebakwangi', "type": 'Desa' },
      { "name": 'Mangunjaya', "type": 'Desa' },
      { "name": 'Mekarjaya', "type": 'Desa' },
      { "name": 'Patrolsari', "type": 'Desa' },
      { "name": 'Pinggirsari', "type": 'Desa' },
      { "name": 'Rancakole', "type": 'Desa' },
      { "name": 'Wargaluyu', "type": 'Desa' },
    ]
  },
  {
    "name": 'BALEENDAH',
    "dapil": 'DAPIL 6',
    "villages": [
      { "name": 'Andir', "type": 'Kelurahan' },
      { "name": 'Baleendah', "type": 'Kelurahan' },
      { "name": 'Bojongmalaka', "type": 'Desa' },
      { "name": 'Jelekong', "type": 'Kelurahan' },
      { "name": 'Malakasari', "type": 'Desa' },
      { "name": 'Manggahang', "type": 'Kelurahan' },
      { "name": 'Rancamanyar', "type": 'Desa' },
      { "name": 'Wargamekar', "type": 'Kelurahan' },
    ]
  },
  {
    "name": 'BANJARAN',
    "dapil": 'DAPIL 7',
    "villages": [
      { "name": 'Banjaran', "type": 'Desa' },
      { "name": 'Banjaran Wetan', "type": 'Desa' },
      { "name": 'Ciapus', "type": 'Desa' },
      { "name": 'Ciherang', "type": 'Desa' },
      { "name": 'Kamasan', "type": 'Desa' },
      { "name": 'Kiangroke', "type": 'Desa' },
      { "name": 'Margahurip', "type": 'Desa' },
      { "name": 'Mekarjaya', "type": 'Desa' },
      { "name": 'Neglasari', "type": 'Desa' },
      { "name": 'Pasirmulya', "type": 'Desa' },
      { "name": 'Sindangpanon', "type": 'Desa' },
      { "name": 'Tarajusari', "type": 'Desa' },
    ]
  },
  {
    "name": 'BOJONGSOANG',
    "dapil": 'DAPIL 3',
    "villages": [
      { "name": 'Bojongsari', "type": 'Desa' },
      { "name": 'Bojongsoang', "type": 'Desa' },
      { "name": 'Buahbatu', "type": 'Desa' },
      { "name": 'Cipagalo', "type": 'Desa' },
      { "name": 'Lengkong', "type": 'Desa' },
      { "name": 'Tegalluar', "type": 'Desa' },
    ]
  },
  {
    "name": 'CANGKUANG',
    "dapil": 'DAPIL 1',
    "villages": [
      { "name": 'Bandasari', "type": 'Desa' },
      { "name": 'Cangkuang', "type": 'Desa' },
      { "name": 'Ciluncat', "type": 'Desa' },
      { "name": 'Jatisari', "type": 'Desa' },
      { "name": 'Nagrak', "type": 'Desa' },
      { "name": 'Pananjung', "type": 'Desa' },
      { "name": 'Tanjungsari', "type": 'Desa' },
    ]
  },
  {
    "name": 'CICALENGKA',
    "dapil": 'DAPIL 4',
    "villages": [
      { "name": 'Babakan Peuteuy', "type": 'Desa' },
      { "name": 'Cicalengka Kulon', "type": 'Desa' },
      { "name": 'Cicalengka Wetan', "type": 'Desa' },
      { "name": 'Cikuya', "type": 'Desa' },
      { "name": 'Dampit', "type": 'Desa' },
      { "name": 'Margaasih', "type": 'Desa' },
      { "name": 'Nagrog', "type": 'Desa' },
      { "name": 'Narawita', "type": 'Desa' },
      { "name": 'Panenjoan', "type": 'Desa' },
      { "name": 'Tanjungwangi', "type": 'Desa' },
      { "name": 'Tenjolaya', "type": 'Desa' },
      { "name": 'Waluya', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIKANCUNG',
    "dapil": 'DAPIL 4',
    "villages": [
      { "name": 'Cihanyir', "type": 'Desa' },
      { "name": 'Cikancung', "type": 'Desa' },
      { "name": 'Cikasungka', "type": 'Desa' },
      { "name": 'Ciluluk', "type": 'Desa' },
      { "name": 'Hegarmanah', "type": 'Desa' },
      { "name": 'Mandalasari', "type": 'Desa' },
      { "name": 'Mekarlaksana', "type": 'Desa' },
      { "name": 'Srirahayu', "type": 'Desa' },
      { "name": 'Tanjunglaya', "type": 'Desa' },
    ]
  },
  {
    "name": 'CILENGKRANG',
    "dapil": 'DAPIL 3',
    "villages": [
      { "name": 'Cilengkrang', "type": 'Desa' },
      { "name": 'Cipanjalu', "type": 'Desa' },
      { "name": 'Ciporeat', "type": 'Desa' },
      { "name": 'Girimekar', "type": 'Desa' },
      { "name": 'Jatiendah', "type": 'Desa' },
      { "name": 'Melatiwangi', "type": 'Desa' },
    ]
  },
  {
    "name": 'CILEUNYI',
    "dapil": 'DAPIL 3',
    "villages": [
      { "name": 'Cibiru Hilir', "type": 'Desa' },
      { "name": 'Cibiru Wetan', "type": 'Desa' },
      { "name": 'Cileunyi Kulon', "type": 'Desa' },
      { "name": 'Cileunyi Wetan', "type": 'Desa' },
      { "name": 'Cimekar', "type": 'Desa' },
      { "name": 'Cinunuk', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIMAUNG',
    "dapil": 'DAPIL 7',
    "villages": [
      { "name": 'Campakamulya', "type": 'Desa' },
      { "name": 'Cikalong', "type": 'Desa' },
      { "name": 'Cimaung', "type": 'Desa' },
      { "name": 'Cipinang', "type": 'Desa' },
      { "name": 'Jagabaya', "type": 'Desa' },
      { "name": 'Malasari', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Pasirhuni', "type": 'Desa' },
      { "name": 'Sukamaju', "type": 'Desa' },
      { "name": 'Warjabakti', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIMENYAN',
    "dapil": 'DAPIL 3',
    "villages": [
      { "name": 'Cibeunying', "type": 'Kelurahan' },
      { "name": 'Ciburial', "type": 'Desa' },
      { "name": 'Cikadut', "type": 'Desa' },
      { "name": 'Cimenyan', "type": 'Desa' },
      { "name": 'Mandalamekar', "type": 'Desa' },
      { "name": 'Mekarmanik', "type": 'Desa' },
      { "name": 'Mekarsaluyu', "type": 'Desa' },
      { "name": 'Padasuka', "type": 'Kelurahan' },
      { "name": 'Sindanglaya', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIPARAY',
    "dapil": 'DAPIL 6',
    "villages": [
      { "name": 'Babakan', "type": 'Desa' },
      { "name": 'Bumiwangi', "type": 'Desa' },
      { "name": 'Ciheulang', "type": 'Desa' },
      { "name": 'Cikoneng', "type": 'Desa' },
      { "name": 'Ciparay', "type": 'Desa' },
      { "name": 'Gunungleutik', "type": 'Desa' },
      { "name": 'Manggungharja', "type": 'Desa' },
      { "name": 'Mekarlaksana', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Pakutandang', "type": 'Desa' },
      { "name": 'Sagaracipta', "type": 'Desa' },
      { "name": 'Sarimahi', "type": 'Desa' },
      { "name": 'Serangmekar', "type": 'Desa' },
      { "name": 'Sumbersari', "type": 'Desa' },
    ]
  },
  {
    "name": 'CIWIDEY',
    "dapil": 'DAPIL 1',
    "villages": [
      { "name": 'Ciwidey', "type": 'Desa' },
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
    "dapil": 'DAPIL 2',
    "villages": [
      { "name": 'Cangkuang Kulon', "type": 'Desa' },
      { "name": 'Cangkuang Wetan', "type": 'Desa' },
      { "name": 'Citeureup', "type": 'Desa' },
      { "name": 'Dayeuhkolot', "type": 'Desa' },
      { "name": 'Pasawahan', "type": 'Kelurahan' },
      { "name": 'Sukapura', "type": 'Desa' },
    ]
  },
  {
    "name": 'IBUN',
    "dapil": 'DAPIL 5',
    "villages": [
      { "name": 'Cibeet', "type": 'Desa' },
      { "name": 'Dukuh', "type": 'Desa' },
      { "name": 'Ibun', "type": 'Desa' },
      { "name": 'Karyalaksana', "type": 'Desa' },
      { "name": 'Laksana', "type": 'Desa' },
      { "name": 'Lampegan', "type": 'Desa' },
      { "name": 'Mekarwangi', "type": 'Desa' },
      { "name": 'Neglasari', "type": 'Desa' },
      { "name": 'Pangguh', "type": 'Desa' },
      { "name": 'Sudi', "type": 'Desa' },
      { "name": 'Talun', "type": 'Desa' },
      { "name": 'Tanggulun', "type": 'Desa' },
    ]
  },
  {
    "name": 'KATAPANG',
    "dapil": 'DAPIL 2',
    "villages": [
      { "name": 'Banyusari', "type": 'Desa' },
      { "name": 'Cilampeni', "type": 'Desa' },
      { "name": 'Gandasari', "type": 'Desa' },
      { "name": 'Katapang', "type": 'Desa' },
      { "name": 'Pangauban', "type": 'Desa' },
      { "name": 'Sangkanhurip', "type": 'Desa' },
      { "name": 'Sukamukti', "type": 'Desa' },
    ]
  },
  {
    "name": 'KERTASARI',
    "dapil": 'DAPIL 6',
    "villages": [
      { "name": 'Cibeureum', "type": 'Desa' },
      { "name": 'Cihawuk', "type": 'Desa' },
      { "name": 'Cikembang', "type": 'Desa' },
      { "name": 'Neglawangi', "type": 'Desa' },
      { "name": 'Resmitingal', "type": 'Desa' },
      { "name": 'Santosa', "type": 'Desa' },
      { "name": 'Sukapura', "type": 'Desa' },
      { "name": 'Tarumajaya', "type": 'Desa' },
    ]
  },
  {
    "name": 'KUTAWARINGIN',
    "dapil": 'DAPIL 1',
    "villages": [
      { "name": 'Buninagara', "type": 'Desa' },
      { "name": 'Cibodas', "type": 'Desa' },
      { "name": 'Cilame', "type": 'Desa' },
      { "name": 'Gajahmekar', "type": 'Desa' },
      { "name": 'Jatisari', "type": 'Desa' },
      { "name": 'Jelegong', "type": 'Desa' },
      { "name": 'Kopo', "type": 'Desa' },
      { "name": 'Kutawaringin', "type": 'Desa' },
      { "name": 'Padasuka', "type": 'Desa' },
      { "name": 'Pameuntasan', "type": 'Desa' },
      { "name": 'Sukamulya', "type": 'Desa' },
    ]
  },
  {
    "name": 'MAJALAYA',
    "dapil": 'DAPIL 5',
    "villages": [
      { "name": 'Biru', "type": 'Desa' },
      { "name": 'Bojong', "type": 'Desa' },
      { "name": 'Majakerta', "type": 'Desa' },
      { "name": 'Majalaya', "type": 'Desa' },
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
    "dapil": 'DAPIL 2',
    "villages": [
      { "name": 'Cigondewah Hilir', "type": 'Desa' },
      { "name": 'Lagadar', "type": 'Desa' },
      { "name": 'Margaasih', "type": 'Desa' },
      { "name": 'Mekar Rahayu', "type": 'Desa' },
      { "name": 'Nanjung', "type": 'Desa' },
      { "name": 'Rahayu', "type": 'Desa' },
    ]
  },
  {
    "name": 'MARGAHAYU',
    "dapil": 'DAPIL 2',
    "villages": [
      { "name": 'Margahayu Selatan', "type": 'Desa' },
      { "name": 'Margahayu Tengah', "type": 'Desa' },
      { "name": 'Sayati', "type": 'Desa' },
      { "name": 'Sukamenak', "type": 'Desa' },
      { "name": 'Sulaeman', "type": 'Kelurahan' },
    ]
  },
  {
    "name": 'NAGREG',
    "dapil": 'DAPIL 2',
    "villages": [
      { "name": 'Bojong', "type": 'Desa' },
      { "name": 'Ciaro', "type": 'Desa' },
      { "name": 'Ciherang', "type": 'Desa' },
      { "name": 'Citaman', "type": 'Desa' },
      { "name": 'Ganjarsabar', "type": 'Desa' },
      { "name": 'Mandalawangi', "type": 'Desa' },
      { "name": 'Nagreg', "type": 'Desa' },
      { "name": 'Nagreg Kendan', "type": 'Desa' },
    ]
  },
  {
    "name": 'PACET',
    "dapil": 'DAPIL 6',
    "villages": [
      { "name": 'Cikawao', "type": 'Desa' },
      { "name": 'Cikitu', "type": 'Desa' },
      { "name": 'Cinanggela', "type": 'Desa' },
      { "name": 'Cipeujeuh', "type": 'Desa' },
      { "name": 'Girimulya', "type": 'Desa' },
      { "name": 'Mandalahaji', "type": 'Desa' },
      { "name": 'Maruyung', "type": 'Desa' },
      { "name": 'Mekarjaya', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Nagrak', "type": 'Desa' },
      { "name": 'Pangauban', "type": 'Desa' },
      { "name": 'Sukarame', "type": 'Desa' },
      { "name": 'Tanjungwangi', "type": 'Desa' },
    ]
  },
  {
    "name": 'PAMEUNGPEUK',
    "dapil": 'DAPIL 7',
    "villages": [
      { "name": 'Bojongkunci', "type": 'Desa' },
      { "name": 'Bojongmanggu', "type": 'Desa' },
      { "name": 'Langonsari', "type": 'Desa' },
      { "name": 'Rancamulya', "type": 'Desa' },
      { "name": 'Rancatungku', "type": 'Desa' },
      { "name": 'Sukasari', "type": 'Desa' },
    ]
  },
  {
    "name": 'PANGALENGAN',
    "dapil": 'DAPIL 7',
    "villages": [
      { "name": 'Banjarsari', "type": 'Desa' },
      { "name": 'Lamajang', "type": 'Desa' },
      { "name": 'Margaluyu', "type": 'Desa' },
      { "name": 'Margamekar', "type": 'Desa' },
      { "name": 'Margamukti', "type": 'Desa' },
      { "name": 'Margamulya', "type": 'Desa' },
      { "name": 'Pangalengan', "type": 'Desa' },
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
    "dapil": 'DAPIL 5',
    "villages": [
      { "name": 'Cigentur', "type": 'Desa' },
      { "name": 'Cijagra', "type": 'Desa' },
      { "name": 'Cipaku', "type": 'Desa' },
      { "name": 'Cipedes', "type": 'Desa' },
      { "name": 'Drawati', "type": 'Desa' },
      { "name": 'Karangtunggal', "type": 'Desa' },
      { "name": 'Loa', "type": 'Desa' },
      { "name": 'Mekarpawitan', "type": 'Desa' },
      { "name": 'Sindangsari', "type": 'Desa' },
      { "name": 'Sukamanah', "type": 'Desa' },
      { "name": 'Sukamantri', "type": 'Desa' },
      { "name": 'Tangsimekar', "type": 'Desa' },
    ]
  },
  {
    "name": 'PASIRJAMBU',
    "dapil": 'DAPIL 1',
    "villages": [
      { "name": 'Cibodas', "type": 'Desa' },
      { "name": 'Cikoneng', "type": 'Desa' },
      { "name": 'Cisondari', "type": 'Desa' },
      { "name": 'Cukanggenteng', "type": 'Desa' },
      { "name": 'Margamulya', "type": 'Desa' },
      { "name": 'Mekarmaju', "type": 'Desa' },
      { "name": 'Mekarsari', "type": 'Desa' },
      { "name": 'Pasirjambu', "type": 'Desa' },
      { "name": 'Sugihmukti', "type": 'Desa' },
      { "name": 'Tenjolaya', "type": 'Desa' },
    ]
  },
  {
    "name": 'RANCABALI',
    "dapil": 'DAPIL 1',
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
    "dapil": 'DAPIL 4',
    "villages": [
      { "name": 'Bojongloa', "type": 'Desa' },
      { "name": 'Bojongsalam', "type": 'Desa' },
      { "name": 'Cangkuang', "type": 'Desa' },
      { "name": 'Haurpugur', "type": 'Desa' },
      { "name": 'Jelegong', "type": 'Desa' },
      { "name": 'Linggar', "type": 'Desa' },
      { "name": 'Nanjungmekar', "type": 'Desa' },
      { "name": 'Rancaekek Kencana', "type": 'Kelurahan' },
      { "name": 'Rancaekek Kulon', "type": 'Desa' },
      { "name": 'Rancaekek Wetan', "type": 'Desa' },
      { "name": 'Sangiang', "type": 'Desa' },
      { "name": 'Sukamanah', "type": 'Desa' },
      { "name": 'Sukamulya', "type": 'Desa' },
      { "name": 'Tegalsumedang', "type": 'Desa' },
    ]
  },
  {
    "name": 'SOLOKANJERUK',
    "dapil": 'DAPIL 5',
    "villages": [
      { "name": 'Bojongemas', "type": 'Desa' },
      { "name": 'Cibodas', "type": 'Desa' },
      { "name": 'Langensari', "type": 'Desa' },
      { "name": 'Padamukti', "type": 'Desa' },
      { "name": 'Panyadap', "type": 'Desa' },
      { "name": 'Rancakasumba', "type": 'Desa' },
      { "name": 'Solokanjeruk', "type": 'Desa' },
    ]
  },
  {
    "name": 'SOREANG',
    "dapil": 'DAPIL 1',
    "villages": [
      { "name": 'Cingcin', "type": 'Desa' },
      { "name": 'Karamatmulya', "type": 'Desa' },
      { "name": 'Pamekaran', "type": 'Desa' },
      { "name": 'Panyirapan', "type": 'Desa' },
      { "name": 'Parungserab', "type": 'Desa' },
      { "name": 'Sadu', "type": 'Desa' },
      { "name": 'Sekarwangi', "type": 'Desa' },
      { "name": 'Soreang', "type": 'Desa' },
      { "name": 'Sukajadi', "type": 'Desa' },
      { "name": 'Sukanagara', "type": 'Desa' },
    ]
  }
]

def seed_data():
    db = SessionLocal()
    try:
        print("Starting seed process...")
        
        # 1. Clear Existing Data
        print("Clearing existing data...")
        try:
            db.query(Attendee).delete()
            db.query(Event).delete()
            db.query(ActivityType).delete()
            db.commit()
            print("Existing data cleared.")
        except Exception as e:
            print(f"Error clearing data: {e}")
            db.rollback()
            return

        # 2. Create Activity Types
        ACTIVITY_TYPES = [
            {"name": "Reses", "max_participants": 150},
            {"name": "Pengawasan Penyelenggaraan Pemerintah", "max_participants": 100},
            {"name": "Pendidikan Demokrasi", "max_participants": 50},
            {"name": "Dialog Wakil Rakyat", "max_participants": 100},
            {"name": "Sapa Budaya", "max_participants": 100},
        ]
        
        activity_type_objects = []
        for activity_data in ACTIVITY_TYPES:
            print(f"Creating ActivityType: {activity_data['name']}")
            activity_type = ActivityType(
                name=activity_data['name'],
                max_participants=activity_data['max_participants']
            )
            db.add(activity_type)
            activity_type_objects.append(activity_type)
        db.commit()
        # Refresh to get IDs
        for at in activity_type_objects:
            db.refresh(at)

        # 3. Iterate through ONE random Kecamatan
        total_activities = 0
        total_attendees = 0
        
        # Select 1 random sub-district
        selected_kec = random.choice(KECAMATAN_DATA)
        # Wrap in a list to keep the loop structure but only process one
        target_kecamatans = [selected_kec]

        for kec in target_kecamatans:
            kec_name = kec['name']
            dapil = kec['dapil']
            villages = kec['villages']
            
            print(f"Processing Kecamatan: {kec_name}")
            
            # Create 2 Activities per Kecamatan
            for i in range(2):
                # Randomly select an activity type
                activity_type = random.choice(activity_type_objects)
                
                # Randomly select a village for the event location
                village_obj = random.choice(villages)
                village_name = village_obj['name']
                
                # Random date within last year or next year
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
                # Random villages but still in that sub-district
                
                attendees_to_add = []
                for _ in range(10):
                    # Random village in same kec
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

    except Exception as e:
        print(f"Critical Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
