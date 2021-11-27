"""
A module to implement ZATCA e-invoice (fatoora)

more information @ https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Pages/default.aspx
"""

from uttlv import TLV
import base64
from hashlib import sha256
import json
from pydantic import validate_arguments
from datetime import datetime

__all__ = ("Fatoora",)


class Fatoora:
    def __init__(
        self,
        seller_name: str,
        tax_number: int,
        invoice_date: str,
        total_amount: float,
        tax_amount: float,
        tags: TLV = TLV(),
    ):
        self.tags = tags
        self.seller_name = seller_name
        self.tax_number = tax_number
        self.invoice_date = invoice_date
        self.total_amount = total_amount
        self.tax_amount = tax_amount


    @classmethod
    def base2dict(cls, base: str) -> dict:
        """Convert base64 to a dictionary

        Args:
            base (str): base64

        Returns:
            dict: dictionary of base64 contents
        """
        tags = TLV()
        decoded = base64.b64decode(base)

        tags = TLV()
        tags.parse_array(bytes(decoded))
        values = (tags[counter].decode() for counter in tags)
        keys = (
            "seller_name",
            "tax_number",
            "invoice_date",
            "total_amount",
            "tax_amount",
        )
        return dict(zip(keys, values))


    @property
    def seller_name(self) -> str:
        return self.tags[1]

    @seller_name.setter
    @validate_arguments
    def seller_name(self, new_value: str) -> None:
        self.tags[0x01] = new_value

    @property
    def tax_number(self) -> str:
        return self.tags[2]

    @tax_number.setter
    @validate_arguments
    def tax_number(self, new_value: int) -> None:
        self.tags[0x02] = str(new_value)

    @property
    def invoice_date(self) -> datetime:
        return datetime.fromtimestamp(str(self.tags[3]))

    @invoice_date.setter
    @validate_arguments
    def invoice_date(self, new_value: str) -> None:
        self.tags[0x03] = str(new_value)

    @property
    def total_amount(self) -> str:
        return self.tags[4]

    @total_amount.setter
    @validate_arguments
    def total_amount(self, new_value: float) -> None:
        self.tags[0x04] = "{:.2f}".format(new_value)

    @property
    def tax_amount(self) -> str:
        return self.tags[5]

    @tax_amount.setter
    @validate_arguments
    def tax_amount(self, new_value: float) -> None:
        self.tags[0x05] = "{:.2f}".format(new_value)



    @property
    def base64(self) -> str:
        """Return base64 of fatoora

        Returns:
            str: base64 of fatoora
        """
        tlv_as_byte_array = self.tags.to_byte_array()
        tlv_as_base64 = base64.b64encode(tlv_as_byte_array).decode()
        return tlv_as_base64


    @property
    def hash(self) -> str:
        """Return the hash of fatoora

        Returns:
            str: hash hexdigest
        """
        return sha256(self.base64.encode()).hexdigest()

    def dict(self) -> dict:
        """Return fatoora details as dictionary

        Returns:
            dict: fatoora details
        """
        return self.__class__.base2dict(self.base64)

    def json(self) -> str:
        """Return fatoora details as json

        Returns:
            str: fatoora details
        """
        return json.dumps(self.dict())
