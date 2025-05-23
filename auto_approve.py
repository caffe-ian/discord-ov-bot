
from openai import OpenAI
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv("MONGO")

client = MongoClient(db_url)
db = client["maindb"]
ccll = db["cardata"]
cll = db['userdata']

s = ccll.find_one({"id": "suggestions"})
suggestions = s["cars"]

client = OpenAI(api_key="")

while True:
    carname = suggestions[0]['name']
    carprice = suggestions[0]['price']
    carspeed = suggestions[0]['speed']
    carrank = suggestions[0]['rank']
    carimage = suggestions[0]['image']
    carspecialty = int(suggestions[0]['specialty'])
    carremarks = suggestions[0]['remarks']
    if carremarks == '':
        carremarks = "No remarks"

    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        instructions="Help approving car suggestions provided by players. Name is correctly provided (Including letter cases)? Price is correct (Convertion: Price of car in real life USD divided by 500, whole number)? Top speed correct (in MPH)?. If price (after conversion) of car is below 100, the rank is Low. if price is between 100 and 500, rank is Average. if price between 500 and 2000, rank is High (MUST FOLLOW). price above 2000 is exotic rank. If car is a classic (Considered as old and worhty for collection), then rank is Classic, and price should be base price (price of release, not current price). If you can't figure out a car's price, reply with the original price. If the car is a concpet car or considered exclusive (For example: only 10 exists, or 1 exists, or only made for ...), then rank is Exclusive. You only need to reply with this format: '[car name]\n[car price]\n[car speed]\n[car rank]'. DO NOT REPLY WITH OTHER EXCESSIVE TEXTS (IMPORTANT). If the car suggestion is a troll (The car doesn't exist in real life or it's a prank), reply with the original information and add a 'Reject troll' below. Also reject if the car is a game car/anime car and add 'Reject virtual'. If everything is alright add 'Approved'. Extra texts are added next line. SEARCH THE INTERNET IF NEEDED. If the car is both classic and exclusive, put classic rank.",
        input=f"Name: {carname}\nPrice: {carprice}\nSpeed: {carspeed}\nRank: {carrank}",
    )

    print(f"---\nName: {carname}\nPrice: {carprice}\nSpeed: {carspeed}\nRank: {carrank}\n{carspecialty}\n{carremarks}\n---")
    print(response.output_text)

    reply = response.output_text.split("\n")
    newname = reply[0].replace(".", "\u002E").strip()
    newprice = reply[1].strip()
    if "N/A" in newprice:
        newprice = int(newprice.split(" ")[0])
    else:
        newprice = int(newprice)
    newspeed = int(reply[2].strip())
    newrank = reply[3].strip()

    while True:
        text = input()
        if text == "":
            print("Couldn't identify command")
        elif text[0] == 'n':
            print(f"Name changed: {newname} > {text[1:]}")
            newname = text[1:].replace(".", "\u002E").strip()
        elif text[0] == "a":
            ccll.update_one({"id": "allcars"},{"$push": {"allcars": newname}})
            if newrank == 'Low':
                ccll.update_one({"id": "lowcar"},{"$push": {"lowcar": newname}})
            elif newrank == 'Average':
                ccll.update_one({"id": "averagecar"},{"$push": {"averagecar": newname}})
            elif newrank == 'High':
                ccll.update_one({"id": "highcar"},{"$push": {"highcar": newname}})
            elif newrank == 'Exotic':
                ccll.update_one({"id": "exoticcar"},{"$push": {"exoticcar": newname}})
            elif newrank == 'Classic':
                ccll.update_one({"id": "classiccar"},{"$push": {"classiccar": newname}})
            elif newrank == 'Exclusive':
                ccll.update_one({"id": "exclusivecar"},{"$push": {"exclusivecar": newname}})

            ccll.update_one({"id": "carprice"},{"$set": {f"carprice.{newname}": newprice}})
            ccll.update_one({"id": "carspeed"},{"$set": {f"carspeed.{newname}": newspeed}})
            ccll.update_one({"id": "carimage"},{"$set": {f"carimage.{newname}": carimage}})

            if newrank == "Low":
                chance = 0.8
            elif newrank == "Average":
                chance = 0.6
            elif newrank == "High":
                chance = 0.4
            elif newrank == "Exotic":
                chance = 0.1
            if newrank == "Classic":
                chance = 0.8

            if newrank != "Exclusive":
                ccll.update_one({"id": "carchance"},{"$set": {f"carchance.{newname}": round(chance,2)}})
            ccll.update_one({"id": "carspecialty"}, {"$set": {f"carspecialty.{newname}": str(carspecialty)}})

            ccll.update_one({"id": "suggestions"}, {"$pull": {"cars": {"name": carname}}})
            cll.update_one({"id": carspecialty}, {"$inc": {"approve": 1}})
            print(f"Car {newname} approved")
            suggestions.pop(0)
            break
        elif text[0] == "p":
            print(f"Price changed: {newprice} > {text[1:]}")
            newprice = int(text[1:])
        elif text[0] == "s":
            print(f"Speed changed: {newspeed} > {text[1:]}")
            newspeed = int(text[1:])
        elif text == 'rej':
            ccll.update_one({"id": "suggestions"}, {"$pull": {"cars": {"name": carname}}})
            print(f"Car {newname} rejected")
            suggestions.pop(0)
            break
        elif text[0] == "r":
            print(f"Rank changed: {newrank} > {text[1:]}")
            newrank = text[1:]
        else:
            print("Couldn't identify command")

# print(completion.choices[0].message);


# response = client.responses.create(
#     model="gpt-4o",
#     input="Write a one-sentence bedtime story about a unicorn."
# )

# print(response.output_text)
