import plistlib
from os.path import expanduser
from pathlib import Path
from time import time

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

homedir = expanduser("~")
homedir = Path(homedir)


@logger.catch
def get_appBundleId(app_name):
    info_plist_path = f'/Applications/{app_name}.app/Contents/Info.plist'
    with open(info_plist_path, 'rb') as plist_file:
        appPlist = plistlib.load(plist_file)
    appBundleId = appPlist['CFBundleIdentifier']
    return appBundleId


# 构建插入或替换的 SQL 语句
# 该语句遵循您提供的 SQLite 命令结构
insert_statement = text("""
    INSERT OR REPLACE INTO access (service, client, client_type, auth_value, auth_reason, auth_version, csreq, policy_id, indirect_object_identifier_type, indirect_object_identifier, indirect_object_code_identity, flags, last_modified, pid, pid_version, boot_uuid, last_reminded)
    VALUES (:service, :client, :client_type, :auth_value, :auth_reason, :auth_version, :csreq, :policy_id, :indirect_object_identifier_type, :indirect_object_identifier, :indirect_object_code_identity, :flags, :last_modified, :pid, :pid_version, :boot_uuid, :last_reminded)
""")


@logger.catch
def add_privilege(database_path, service, client):
    database_path = Path(database_path).as_posix()
    engine = create_engine(f'sqlite:///{database_path}')

    # 第3步：插入或替换记录
    Session = sessionmaker(bind=engine)
    session = Session()

    current_timestamp = int(time())
    session.execute(insert_statement, {
        'service': service,
        'client': client,
        'client_type': 0,
        'auth_value': 2,
        'auth_reason': 4,
        'auth_version': 1,
        'csreq': None,
        'policy_id': None,
        'indirect_object_identifier_type': 0,
        'indirect_object_identifier': 'UNUSED',
        'indirect_object_code_identity': None,
        'flags': 0,
        'last_modified': current_timestamp,
        'pid': None,
        'pid_version': None,
        'boot_uuid': 'UNUSED',
        'last_reminded': 0
    })
    session.commit()

    # 关闭 session
    session.close()


service = 'kTCCServiceMicrophone'  # 麦克风
# service = 'kTCCServiceScreenCapture'  # 录屏
# service = 'kTCCServiceAccessibility'  # 辅助功能
# service = 'kTCCServiceCamera'  # 摄像头


if __name__ == '__main__':
    database_path = homedir / 'Library' / 'Application Support' / 'com.apple.TCC' / 'TCC.db'
    app_name = 'Boson'
    client = get_appBundleId(app_name)
    add_privilege(database_path, service, client)
