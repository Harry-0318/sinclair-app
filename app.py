from flask import Flask, request, render_template_string
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<title>Sinclair Calculator</title>
<h2>Sinclair Safety Check</h2>
<form method=post>
  Target BW: <input type=text name=targets_bw><br><br>
  Target LW: <input type=text name=targets_lw><br><br>
  Your BW: <input type=text name=your_bw><br><br>
  Your LW: <input type=text name=your_lw><br><br>
  Safe Margin: <input type=text name=margin_needed><br><br>
  <input type=submit value=Check>
</form>
{% if result %}
<h3>{{ result }}</h3>
{% endif %}
'''

@app.route("/", methods=["GET", "POST"])
def sinclair():
    result = None
    if request.method == "POST":
        targets_bw = request.form["targets_bw"]
        targets_lw = request.form["targets_lw"]
        your_bw = request.form["your_bw"]
        your_lw = float(request.form["your_lw"])
        margin_needed = float(request.form["margin_needed"])

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Optional: remove this if you want to see the browser
        driver = webdriver.Chrome(options=options)

        try:
            driver.get("https://iwf.sport/weightlifting_/sinclair-coefficient/")
            time.sleep(3)

            bw = driver.find_element(By.ID, "sinclair_weight")
            lw = driver.find_element(By.ID, "sinclair_total")
            final = driver.find_element(By.ID, "sinclair_result")
            submit = driver.find_element(By.ID, "sinclair_submit")

            bw.clear()
            lw.clear()
            bw.send_keys(targets_bw)
            lw.send_keys(targets_lw)
            submit.click()
            time.sleep(2)
            sinclair_target = float(final.text.strip('YOUR SINCLAIR IS:\n'))

            while True:
                bw.clear()
                lw.clear()
                bw.send_keys(your_bw)
                lw.send_keys(str(your_lw))
                submit.click()
                time.sleep(1)
                sinclair_your = float(final.text.strip('YOUR SINCLAIR IS:\n'))
                if sinclair_your > sinclair_target + margin_needed:
                    result = f"✅ Safe Zone! Bodyweight: {your_bw} kg | Lift: {your_lw} kg | Sinclair: {sinclair_your:.2f}"
                    break
                else:
                    your_lw += 1.0

        except Exception as e:
            result = f"❌ Error: {e}"
        finally:
            driver.quit()

    return render_template_string(TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
