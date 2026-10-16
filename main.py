from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinjax import Catalog, JinjaX
from sqlalchemy import String, cast, func
from sqlalchemy.orm import Session

from database import get_db
from models import AnnouncedPUResult, PollingUnit, LGA, Ward, State, Party

app = FastAPI(title="Bincom Election Results")

templates = Jinja2Templates(directory="templates")
templates.env.add_extension(JinjaX)

catalog = Catalog(jinja_env=templates.env)
catalog.add_folder("templates/components")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "unit_id": None,
            "polling_unit": None,
            "results": [],
            "error": None,
        },
    )


@app.get("/polling-unit-results", response_class=HTMLResponse)
def get_polling_unit_results(
    request: Request,
    unit_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    polling_unit = db.get(PollingUnit, unit_id)

    if polling_unit is None:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "unit_id": unit_id,
                "polling_unit": None,
                "results": [],
                "error": f"Polling unit {unit_id} was not found.",
            },
            status_code=404,
        )

    results = (
        db.query(AnnouncedPUResult)
        .filter(AnnouncedPUResult.polling_unit_uniqueid == str(unit_id))
        .order_by(AnnouncedPUResult.party_abbreviation)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "unit_id": unit_id,
            "polling_unit": polling_unit,
            "results": results,
            "error": None,
        },
    )


@app.get("/lga-results", response_class=HTMLResponse)
def get_lga_results(
    request: Request,
    lga_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):

    lgas = (
        db.query(LGA)
        .order_by(LGA.lga_name)
        .all()
    )

    total_polling_units = None
    results = []
    selected_lga = None
    message = None

    if lga_id is not None:
        selected_lga = db.query(LGA).filter(
            LGA.uniqueid == lga_id
        ).first()

        if selected_lga is None:
            message = "The selected LGA was not found."
        else:
            total_polling_units = (
                db.query(func.count(PollingUnit.uniqueid))
                .filter(PollingUnit.lga_id == lga_id)
                .scalar()
            )

            results = (
                db.query(
                    AnnouncedPUResult.party_abbreviation,
                    func.sum(
                        AnnouncedPUResult.party_score
                    ).label("total_score"),
                )
                .join(
                    PollingUnit,
                    AnnouncedPUResult.polling_unit_uniqueid
                    == cast(PollingUnit.uniqueid, String(50)),
                )
                .filter(PollingUnit.lga_id == lga_id)
                .group_by(AnnouncedPUResult.party_abbreviation)
                .order_by(AnnouncedPUResult.party_abbreviation)
                .all()
            )

            if not total_polling_units:
                message = "No polling units were found for this LGA."
            elif not results:
                message = "No polling-unit results have been recorded for this LGA."

    return templates.TemplateResponse(
        request=request,
        name="lga_results.html",
        context={
            "lgas": lgas,
            "lga_id": lga_id,
            "selected_lga": selected_lga,
            "total_polling_units": total_polling_units,
            "results": results,
            "message": message,
        },
    )


@app.get("/api/lgas/{state_id}")
def get_lgas(state_id: int, db: Session = Depends(get_db)):
    return [
        {"id": lga.uniqueid, "name": lga.lga_name}
        for lga in db.query(LGA)
        .filter(LGA.state_id == state_id)
        .order_by(LGA.lga_name)
        .all()
    ]


@app.get("/api/wards/{lga_id}")
def get_wards(lga_id: int, db: Session = Depends(get_db)):
    return [
        {"id": ward.uniqueid, "name": ward.ward_name}
        for ward in db.query(Ward)
        .filter(Ward.lga_id == lga_id)
        .order_by(Ward.ward_name)
        .all()
    ]



@app.get("/polling-units/new", response_class=HTMLResponse)
def new_polling_unit(
    request: Request,
    db: Session = Depends(get_db),
):
    states = db.query(State).order_by(State.state_name).all()
    parties = db.query(Party).order_by(Party.partyname).all()

    return templates.TemplateResponse(
        request=request,
        name="add_polling_unit.html",
        context={
            "states": states,
            "parties": parties,
            "error": None,
        },
    )

@app.post("/polling-units/create", response_class=HTMLResponse)
def create_polling_unit(
    request: Request,
    lga_id: int = Form(...),
    ward_id: int = Form(...),
    polling_unit_name: str = Form(...),
    party_abbreviations: list[str] = Form(...),
    party_scores: list[int] = Form(...),
    db: Session = Depends(get_db),
):
    print("LGA ID received:", lga_id)
    print("Ward ID received:", ward_id)
    try:
        if len(party_abbreviations) != len(party_scores):
            raise ValueError("Party names and scores do not match.")

        if not polling_unit_name.strip():
            raise ValueError("Polling unit name is required.")

        if any(score < 0 for score in party_scores):
            raise ValueError("Vote scores cannot be negative.")

        ward = (
            db.query(Ward)
            .filter(
                Ward.uniqueid == ward_id,
                Ward.lga_id == lga_id,
            )
            .first()
        )

        if not ward:
            raise ValueError("The selected ward does not belong to this LGA.")

        parties = db.query(Party).all()
        valid_party_ids = {party.partyid for party in parties}

        if (
            len(set(party_abbreviations)) != len(party_abbreviations)
            or not set(party_abbreviations).issubset(valid_party_ids)
        ):
            raise ValueError("Invalid or duplicate party submitted.")

        last_polling_unit_id = (
            db.query(func.max(PollingUnit.polling_unit_id)).scalar()
        )
        next_polling_unit_id = (
            (last_polling_unit_id or 0) + 1
        )

        polling_unit = PollingUnit(
            polling_unit_id=next_polling_unit_id,
            lga_id=lga_id,
            ward_id=ward_id,
            polling_unit_name=polling_unit_name.strip(),
        )

        db.add(polling_unit)
        db.flush()

        client_ip = (
            request.client.host
            if request.client
            else "127.0.0.1"
        )
        for abbreviation, score in zip(
            party_abbreviations, party_scores
        ):
            result = AnnouncedPUResult(
                polling_unit_uniqueid=polling_unit.uniqueid,
                party_abbreviation=abbreviation,
                party_score=score,
                entered_by_user="admin",
                date_entered=datetime.now(),
                user_ip_address=client_ip,
            )
            db.add(result)


        db.commit()

        return RedirectResponse(
            url="/",
            status_code=303,
        )

    except ValueError as exc:
        db.rollback()

        states = db.query(State).order_by(State.state_name).all()
        parties = db.query(Party).order_by(Party.partyname).all()

        return templates.TemplateResponse(
            request=request,
            name="add_polling_unit.html",
            context={
                "states": states,
                "parties": parties,
                "error": str(exc),
            },
            status_code=400,
        )

    except Exception:
        db.rollback()
        raise







