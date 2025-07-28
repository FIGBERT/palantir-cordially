from cordially_sdk.ontology.objects import Event, Recipient
from fasthtml import ft

DELETE_STYLE = "background-color: #d93526; border-color: #d93526;"


def generic_err() -> ft.FT:
    return ft.Titled(
        "Error",
        ft.P("Not sure what happened here."),
        ft.A(ft.Button("Escape"), href="/admin"),
    )


def permission_err() -> ft.FT:
    return ft.Titled(
        "None shall pass.",
        ft.P("Are you lost?"),
        ft.A(ft.Button("Flee"), href="/"),
    )


def event(evt: Event | None = None, count: int = 0) -> ft.FT:
    form_elems: list[ft.FT] = []
    if evt:
        form_elems.append(ft.Input(type="hidden", name="id", value=evt.id))

    form_elems.extend(
        [
            ft.Label(
                "Name",
                ft.Input(
                    type="text",
                    id="name",
                    name="name",
                    placeholder=f"Event {count}",
                    required=True,
                    value=f"{evt.name if evt else ''}",
                ),
                fr="name",
            ),
            ft.Label(
                "Location",
                ft.Input(
                    type="text",
                    id="location",
                    name="location",
                    placeholder="Chateau Bleu",
                    required=True,
                    value=f"{evt.location if evt else ''}",
                ),
                fr="location",
            ),
            ft.Div(
                ft.Label(
                    "Start",
                    ft.Input(
                        type="datetime-local",
                        id="when",
                        name="when",
                        required=True,
                        value=f"{evt.when.strftime('%Y-%m-%dT%H:%M:%S') if evt and evt.when else ''}",
                    ),
                    fr="when",
                ),
                ft.Label(
                    "End",
                    ft.Input(
                        type="datetime-local",
                        id="end",
                        name="end",
                        value=f"{evt.end.strftime('%Y-%m-%dT%H:%M:%S') if evt and evt.end else ''}",
                    ),
                    fr="end",
                ),
                cls="grid",
            ),
            ft.Div(
                ft.Label(
                    "Food",
                    ft.Input(
                        type="text",
                        id="food",
                        name="food",
                        placeholder="Homemade feast",
                        value=f"{evt.food if evt else ''}",
                    ),
                    fr="food",
                ),
                ft.Label(
                    "Dress Code",
                    ft.Input(
                        type="text",
                        id="dress_code",
                        name="dress_code",
                        placeholder="Black tie",
                        value=f"{evt.dress_code if evt else ''}",
                    ),
                    fr="dress_code",
                ),
                cls="grid",
            ),
        ]
    )

    if evt:
        form_elems.extend(
            [
                ft.Button(
                    "Save", style="margin-inline-end: 1rem;", hx_post="/event/edit"
                ),
                ft.Button(
                    "Delete",
                    style=DELETE_STYLE,
                    hx_delete="/event",
                    hx_confirm="Are you sure you want to delete the event?",
                ),
            ]
        )
    else:
        form_elems.extend(
            [
                ft.Button(
                    "Create",
                    style="margin-inline-end: 1rem;",
                    hx_post="/event/create",
                    hx_target="body",
                ),
                ft.Button(
                    "Back", cls="secondary outline", hx_get="/admin", hx_target="body"
                ),
            ]
        )

    return ft.Titled(
        f"{'Edit' if evt else 'New'} Event",
        ft.Form(*form_elems),
    )


def recipient(rcp: Recipient | None = None) -> ft.FT:
    form_elems = []
    if rcp:
        form_elems.append(ft.Input(type="hidden", name="id", value=rcp.id))
    form_elems.extend(
        [
            ft.Label(
                "Honorific",
                ft.Input(
                    type="text",
                    id="hnr",
                    name="hnr",
                    placeholder="Prof.",
                    value=f"{rcp.honorific if rcp else ''}",
                ),
                fr="hnr",
            ),
            ft.Label(
                "Name",
                ft.Input(
                    type="text",
                    id="name",
                    name="name",
                    placeholder="Diamond",
                    value=f"{rcp.name if rcp else ''}",
                ),
                fr="name",
            ),
        ]
    )
    if rcp:
        form_elems.extend(
            [
                ft.Button(
                    "Save",
                    style="margin-inline-end: 1rem;",
                    hx_post="/recipient/edit",
                    hx_target="body",
                ),
                ft.Button(
                    "Delete",
                    style=DELETE_STYLE,
                    hx_delete="/recipient",
                    hx_confirm="Are you sure you want to delete the recipient?",
                ),
            ]
        )
    else:
        form_elems.extend(
            [
                ft.Button(
                    "Create",
                    style="margin-inline-end: 1rem;",
                    hx_post="/recipient/create",
                    hx_target="body",
                ),
                ft.Button(
                    "Back",
                    cls="secondary outline",
                    hx_get="/recipients",
                    hx_target="body",
                ),
            ]
        )

    return ft.Titled(
        f"{'Edit' if rcp else 'New'} Recipient",
        ft.Form(*form_elems),
    )


def add_recipient_button(event: str | None, rcp: str | None) -> ft.FT:
    return ft.Button(
        "+",
        hx_post=f"/rsvp?evt={event}&rcp={rcp}",
        hx_target="closest div",
        hx_swap="outerHTML",
        hx_trigger="click",
        style="padding: revert; line-height: unset; margin-inline-end: 1rem;",
    )


def remove_recipient_button(rsvp: str | None) -> ft.FT:
    return ft.Button(
        "-",
        hx_delete=f"/rsvp?id={rsvp}",
        hx_target="closest div",
        hx_swap="outerHTML",
        hx_trigger="click",
        style=f"{DELETE_STYLE} padding: revert; line-height: unset; margin-inline-end: 1rem;",
    )


def recipient_show_link_button(rsvp: str | None) -> ft.FT:
    return ft.Span(
        ft.Button(
            "Link",
            hx_get=f"/event/link/show?id={rsvp}",
            hx_target=f"closest span",
            hx_swap="outerHTML",
            hx_trigger="click",
            style="padding: revert; line-height: unset;",
            cls="secondary",
        ),
    )


def recipient_link(rsvp: str) -> ft.FT:
    return ft.Span(
        ft.Input(type="text", value=f"/view/{rsvp}", disabled=True),
        ft.Button(
            "Hide",
            hx_get=f"/event/link/hide?id={rsvp}",
            hx_target=f"closest span",
            hx_swap="outerHTML",
            hx_trigger="click",
            style="padding: revert; line-height: unset;",
            cls="secondary",
        ),
        role="group",
        style="margin-block-start: 1rem;",
    )


def rsvp_button(id: str, cancel: bool = False) -> ft.FT:
    return ft.Button(
        f"{'Cancel' if cancel else 'RSVP'}",
        hx_post=f"/confirm?id={id}&val={not cancel}",
        hx_swap="outerHTML",
        style=f"{DELETE_STYLE if cancel else ''}display: block; margin-inline: auto;",
    )
