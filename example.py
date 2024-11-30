from captcha_solver.geetest.solvers import slider_solver


def main():
    with open("page.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    print(slider_solver(html_content=html_content))

if __name__ == "__main__":
    main()