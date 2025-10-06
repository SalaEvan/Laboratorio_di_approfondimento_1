from flask import Blueprint, render_template, request, flash 
from flask_login import current_user
from models.connection import db
from models.model import StairCalculation, AppConfig

app = Blueprint('api', __name__)

@app.route('/calculation', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Massimi accettati in cm
            MAX_HEIGHT_CM = 4200
            MAX_LENGTH_CM = 5000

            # Leggi input e unità
            height_unit = request.form.get('height_unit', 'cm')
            length_unit = request.form.get('length_unit', 'cm')

            raw_height = float(request.form['height'])
            raw_length = float(request.form['length'])

            # Conversione in cm per uniformità
            if height_unit == 'm':
                total_height_cm = raw_height * 100
            else:
                total_height_cm = raw_height

            if length_unit == 'm':
                total_length_cm = raw_length * 100
            else:
                total_length_cm = raw_length

            # Controllo limiti massimi
            if total_height_cm > MAX_HEIGHT_CM or total_length_cm > MAX_LENGTH_CM:
                flash(f"Dimensioni troppo grandi: altezza max {MAX_HEIGHT_CM/100} m, lunghezza max {MAX_LENGTH_CM/100} m.")
                return render_template('index.html')

            # Conversione per visualizzazione (display)
            if total_height_cm >= 100:
                total_height_display = total_height_cm / 100
                height_display_unit = 'm'
            else:
                total_height_display = total_height_cm
                height_display_unit = 'cm'

            if total_length_cm >= 100:
                total_length_display = total_length_cm / 100
                length_display_unit = 'm'
            else:
                total_length_display = total_length_cm
                length_display_unit = 'cm'

            # Calcoli sempre in metri
            total_height = total_height_cm / 100
            total_length = total_length_cm / 100

            # Vincoli ergonomici
            min_steps = max(1, int((total_height / 0.20) + 0.9999))
            max_steps = max(1, int((total_length / 0.23) + 0.0001))

            if min_steps > max_steps:
                flash("Dimensioni non fattibili con i vincoli ergonomici.")
                return render_template('index.html')

            num_steps = max(1, round(total_height / 0.17))
            if num_steps < min_steps:
                num_steps = min_steps
            if num_steps > max_steps:
                num_steps = max_steps

            riser_height = total_height / num_steps
            tread_length = total_length / num_steps

            cfg = db.session.query(AppConfig).get(1)

            # Controllo rigido su overhang_factor
            if getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'role', None) == 'admin':
                override = request.form.get('overhang_factor', '').strip()
                try:
                    value = float(override)
                    if 0 < value <= 0.3:
                        overhang_factor = value
                    else:
                        raise ValueError("Overhang factor fuori range")
                except (ValueError, TypeError):
                    overhang_factor = (cfg.overhang_factor if cfg else 0.16)
            else:
                overhang_factor = (cfg.overhang_factor if cfg else 0.16)

            # Calcolo sporgenza e pedata con sporgenza
            overhang = tread_length * overhang_factor
            tread_with_overhang = tread_length + overhang

            # Controllo che pedata con sporgenza non superi la lunghezza disponibile
            if tread_with_overhang > total_length:
                flash("Dimensioni non compatibili: la lunghezza pedata con sporgenza supera la lunghezza disponibile.")
                return render_template('index.html')

            # Controllo vincoli ergonomici alzata e pedata
            if riser_height > 0.20 or tread_length < 0.23:
                flash("Dimensioni non fattibili con i vincoli ergonomici (alzata o pedata fuori range).")
                return render_template('index.html')

            if getattr(current_user, 'is_authenticated', False):
                calc = StairCalculation(
                    user_id=current_user.id,
                    total_height=total_height,
                    total_length=total_length,
                    num_steps=num_steps,
                    riser_height=riser_height,
                    tread_length=tread_length,
                    overhang=overhang,
                )
                db.session.add(calc)
                db.session.commit()

            return render_template(
                'result.html',
                num_steps=num_steps,
                riser_height=round(riser_height * 100, 1),
                tread_length=round(tread_length * 100, 1),           
                overhang=round(overhang * 100, 1),
                tread_with_overhang=round(tread_with_overhang * 100, 1), 
                total_length=round(total_length_display, 2),
                total_height=round(total_height_display, 2),
                length_unit=length_display_unit,
                height_unit=height_display_unit,
            )
        except ValueError:
            return "Inserisci valori numerici validi!", 400

    return render_template('index.html')
