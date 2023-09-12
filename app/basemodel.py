from pydantic import BaseModel


class Post(BaseModel):
    """ Data schame for post entities """
    title: str
    content: str
    published: bool = True


class PersonalInfo(BaseModel):
    firstname: str
    lastname: str
    gender: str
    birthdate: str
    phone: str
    email: str


class AddressDegree(BaseModel):
    zipcode: str
    stateProvince: str
    townCity: str
    degree: str
    course: str
    program: str
    institution: str
