import os
from datetime import datetime

from cordially_sdk import FoundryClient, UserTokenAuth
from cordially_sdk.ontology.objects import Event, Letter, Recipient, Rsvp

auth = UserTokenAuth(token=os.environ["FOUNDRY_TOKEN"])
client = FoundryClient(auth=auth, hostname="https://figbert.usw-18.palantirfoundry.com")


def get_user() -> str:
    resp = client.foundry_sdk.admin.User.get_current().given_name
    return resp if resp else "User"


def events() -> list[Event]:
    return list(
        client.ontology.objects.Event.order_by(Event.object_type.when.asc()).iterate()
    )


def event_by_id(id: str | None) -> Event | None:
    return client.ontology.objects.Event.get(id)


def event_by_name(name: str) -> Event:
    return list(
        client.ontology.objects.Event.where(Event.object_type.name == name).iterate()
    )[0]


def create_event(
    name: str,
    location: str,
    when: datetime,
    end: datetime,
    food: str,
    dress_code: str,
):
    _ = client.ontology.actions.create_event(
        name=name,
        location=location,
        accepting_invites=True,
        when=when,
        end=end,
        food=food,
        dress_code=dress_code,
    )


def edit_event(
    id: str,
    name: str,
    location: str,
    when: datetime,
    end: datetime,
    food: str,
    dress_code: str,
):
    _ = client.ontology.actions.edit_event(
        event=id,
        name=name,
        location=location,
        accepting_invites=True,
        when=when,
        end=end,
        food=food,
        dress_code=dress_code,
    )


def delete_event(id: str):
    _ = client.ontology.actions.delete_event(event=id)


def letter_by_id(id: str) -> Letter | None:
    return client.ontology.objects.Letter.get(id)


def letter_by_event(id: str | None) -> Letter:
    return list(
        client.ontology.objects.Letter.where(
            Letter.object_type.event_id == id
        ).iterate()
    )[0]


def create_letter(event: str):
    _ = client.ontology.actions.create_letter(event_id=event, content="")


def edit_letter(id: str, content: str):
    _ = client.ontology.actions.edit_letter(letter=id, content=content)


def delete_letter(id: str):
    _ = client.ontology.actions.delete_letter(letter=id)


def recipients() -> list[Recipient]:
    return list(client.ontology.objects.Recipient.iterate())


def recipient(id: str | None) -> Recipient | None:
    return client.ontology.objects.Recipient.get(id)


def create_recipient(name: str, hnr: str):
    _ = client.ontology.actions.create_recipient(name=name, honorific=hnr)


def edit_recipient(id: str, name: str, hnr: str):
    _ = client.ontology.actions.edit_recipient(recipient=id, name=name, honorific=hnr)


def delete_recipient(id: str):
    _ = client.ontology.actions.delete_recipient(recipient=id)


def create_recipient_letter_link(rcp: str, ltr: str):
    _ = client.ontology.actions.create_recipient_lt_gt_letter(
        recipients=rcp, letter=ltr
    )


def delete_recipient_letter_link(rcp: str, ltr: str):
    _ = client.ontology.actions.delete_recipient_lt_gt_letter(
        recipients=rcp, letter=ltr
    )


def member_of_event(rcp: Recipient, letter: str) -> bool:
    return len(list(rcp.letter().where(Letter.object_type.id == letter).iterate())) > 0


def create_rsvp(event: str, rcp: str):
    _ = client.ontology.actions.create_rsvp(event_id=event, recipient_id=rcp)


def rsvps_between(event: str | None, rcp: str | None) -> list[Rsvp]:
    return list(
        client.ontology.objects.Rsvp.where(Rsvp.object_type.event_id == event)
        .where(Rsvp.object_type.recipient_id == rcp)
        .iterate()
    )


def rsvps_for(event: str) -> list[Rsvp]:
    return list(
        client.ontology.objects.Rsvp.where(Rsvp.object_type.event_id == event).iterate()
    )


def delete_rsvp(obj: Rsvp):
    _ = client.ontology.actions.delete_rsvp(rsvp=obj)
