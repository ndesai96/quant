from lambda_function import lambda_handler

def main():
    response = lambda_handler(None, None)
    print(response)

if __name__ == "__main__":
    main()  