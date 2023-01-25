from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime


Model = declarative_base(name="Model")


class UserLogin(Model):
    """UserLogin data model.

    Attributes:
        user_id: String containing the user ID.
        device_type: String containing the device type.
        masked_ip: Encoded string containing the IP address.
        masked_device_id: Encoded string containing the device ID.
        locale: String containing the locale.
        app_version: Integer containing the app version.
        create_date: Datetime containing when the data was created.
    """

    __tablename__ = "user_logins"
    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", String(128))
    device_type = Column("device_type", String(32))
    masked_ip = Column("masked_ip", String(256))
    masked_device_id = Column("masked_device_id", String(256))
    locale = Column("locale", String(32))
    app_version = Column("app_version", Integer())
    create_date = Column("create_date", DateTime())

    def __init__(
        self,
        user_id,
        device_type,
        masked_ip,
        masked_device_id,
        locale,
        app_version,
        create_date,
    ):
        self.user_id = user_id
        self.device_type = device_type
        self.masked_ip = masked_ip
        self.masked_device_id = masked_device_id
        self.locale = locale
        self.app_version = app_version
        self.create_date = create_date

    def __repr__(self):
        return f"UserLogin({self.user_id}, {self.device_type}, {self.masked_ip}, {self.masked_device_id}, {self.locale}, {self.app_version}, {self.create_date})"

    def __str__(self):
        return f"({self.user_id}, {self.device_type}, {self.masked_ip}, {self.masked_device_id}, {self.locale}, {self.app_version}, {self.create_date})"


def create_user_login_model(d: dict):
    """Converts a dictionary to a UserLogin data model.

    Args:
        d: A dictionary with keys user_id, app_version,
        device_type, masked_ip, locale, masked_device_id,
        and create_date.

    Returns:
        u: An instance of the UserLogin model.
    """

    u = UserLogin(
        user_id=d["user_id"],
        device_type=d["device_type"],
        masked_ip=d["masked_ip"],
        masked_device_id=d["masked_device_id"],
        locale=d["locale"],
        app_version=d["app_version"],
        create_date=d["create_date"],
    )

    return u
