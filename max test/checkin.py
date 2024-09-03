def check_direction(daten_direction):
    last_transportstation = None  # Track the last transport station

    for index, item in enumerate(daten_direction):
        value_in_out = item['direction']
        current_transportstation = item.get('transportstation', '')  # Get current transport station

        if index % 2 == 0:  # Expected 'in'
            if value_in_out == "'in'":
                # Check for repeated check-ins into the same cooling house
                if last_transportstation == current_transportstation:
                    label_direction.config(text=f"Fehler: Wiederholtes Einchecken in {current_transportstation}!", fg="red")
                    return False
                print(value_in_out, "i.o.")
            else:
                label_direction.config(text='Fehler: Zweimal nacheinander ausgecheckt!', fg="red")
                return False
        else:  # Expected 'out'
            if value_in_out == "'out'":
                print(value_in_out, "i.o.")
            else:
                label_direction.config(text='Fehler: Zweimal nacheinander eingecheckt!', fg="red")
                return False

        # Update the last transport station after processing the 'in' direction
        if value_in_out == "'in'":
            last_transportstation = current_transportstation

    last_line = daten_direction[-1]
    last_direction = last_line['direction']
    if last_direction == "'out'":
        print("Am Ende wurde ausgecheckt")
    else:
        label_direction.config(text='Auschecken am Ende fehlt', fg="red")
        return False

    return True
