import matplotlib.pyplot as plt

def focus_graph():
    try:
        with open("focus.txt", "r") as file:
            content = file.read()

        content = content.split(",")
        x1 = list(range(len(content)))
        y1 = [float(i) for i in content]

        print(content)

        plt.plot(x1, y1, color="red", marker="o")
        plt.title("YOUR FOCUSED TIME", fontsize=16)
        plt.xlabel("Times", fontsize=14)
        plt.ylabel("Focus Time", fontsize=14)
        plt.grid()
        plt.show()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    focus_graph()