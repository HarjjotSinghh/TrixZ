import asyncio, discord, datetime, re
from geopy.geocoders import Nominatim
from discord.ext import commands
from _Utils import Message, Nullify, DL
from bot import main_color, tick, cross
import requests, json

config1 = open('config.json', 'r')
config = json.load(config1)

def setup(client):
    client.add_cog(weather(client))

class weather(commands.Cog):
    """Weather commands which are accessible to all members of the server!"""
    def __init__(self, client):
        self.client = client
        self.key = config["WEATHER_API_KEY"]
        self.geo = Nominatim(user_agent=config["USER_AGENT"])

    def _get_output(self, w_text):
        if "tornado" in w_text.lower():
            return "🌪️ " + w_text
        if any(x in w_text.lower() for x in ["hurricane", "tropical"]):
            return "🌀 " + w_text
        if any(x in w_text.lower() for x in ["snow", "flurries", "hail"]):
            return "🌨️ " + w_text
        if "thunder" in w_text.lower():
            return "⛈️ " + w_text
        if any(x in w_text.lower() for x in ["rain", "drizzle", "showers", "sleet"]):
            return "🌧️ " + w_text
        if "cold" in w_text.lower():
            return "❄️ " + w_text
        if any(x in w_text.lower() for x in ["windy", "blustery", "breezy"]):
            return "🌬️ " + w_text
        if "mostly cloudy" in w_text.lower():
            return "⛅ " + w_text
        if any(x in w_text.lower() for x in ["partly cloudy", "scattered clouds", "few clouds", "broken clouds"]):
            return "🌤️ " + w_text
        if any(x in w_text.lower() for x in ["cloudy", "clouds"]):
            return "☁️ " + w_text
        if "fair" in w_text.lower():
            return "🌄 " + w_text
        if any(x in w_text.lower() for x in ["hot", "sunny", "clear"]):
            return "☀️ " + w_text
        if any(x in w_text.lower() for x in ["dust", "foggy", "haze", "smoky"]):
            return "️🌫️ " + w_text
        return w_text

    def _f_to_c(self, f):
        return int((int(f) - 32) / 1.8)

    def _c_to_f(self, c):
        return int((int(c) * 1.8) + 32)

    def _c_to_k(self, c):
        return int(int(c) + 273)

    def _k_to_c(self, k):
        return int(int(k) - 273)

    def _f_to_k(self, f):
        return self._c_to_k(self._f_to_c(int(f)))

    def _k_to_f(self, k):
        return self._c_to_f(self._k_to_c(int(k)))

    def get_weather_text(self, r={}, show_current=True):
        # Returns a string representing the weather passed
        main = r["main"]
        weath = r["weather"]
        tc = self._k_to_c(main["temp"])
        tf = self._c_to_f(tc)
        minc = self._k_to_c(main["temp_min"])
        minf = self._c_to_f(minc)
        maxc = self._k_to_c(main["temp_max"])
        maxf = self._c_to_f(maxc)
        weath_list = []
        for x, y in enumerate(weath):
            d = y["description"]
            if x == 0:
                d = d.title()
            weath_list.append(self._get_output(d))
        condition = ", ".join(weath_list)
        if show_current:
            desc = "{} °F ({} °C),\n\n".format(tf, tc)
        else:
            desc = ""
        desc += "{}\n{} °C - {} °C\n\n".format(
            condition, maxc, minc
        )
        return desc

    @commands.command(name="weather", help="Tells the current weather of the city mentioned.")
    @commands.cooldown(1, 5)
    async def weather(self, ctx, *, city: str):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = city
        complete_url = base_url + "appid=" + self.key + "&q=" + city_name
        response = requests.get(complete_url)
        x = response.json()
        channel = ctx.message.channel
        if x["cod"] != "404":
            async with channel.typing():
                city_name = re.sub(r'([^\s\w]|_)+', '', city_name)
                location = self.geo.geocode(city_name)
                y = x["main"]
                title = location.address
                current_temperature = y["temp"]
                current_temperature_celsiuis = str(round(current_temperature - 273.15))
                current_pressure = y["pressure"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                embed = discord.Embed(title=title,
                                      color=main_color)
                embed.add_field(name="Descripition", value="**" + self._get_output(weather_description).title() + "**", inline=False)
                embed.add_field(name="Temperature(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
                embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
                embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
                embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
                await ctx.message.add_reaction(tick)
                await channel.send(embed=embed)
        else:
            await ctx.message.add_reaction(cross)
            await channel.send("City not found.")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5)
    async def forecast(self, ctx, *, city_name=None):
        """Gets the weather forecast of the next 5 days of the city mentioned!"""
        if city_name == None:
            await ctx.send("Usage: `{}forecast [city_name]`".format(ctx.prefix))
            return

        city_name = re.sub(r'([^\s\w]|_)+', '', city_name)
        location = self.geo.geocode(city_name)
        if location == None:
            await Message.EmbedText(
                title='City Not Found.',
                color=discord.Color.red()
            ).send(ctx)
            return

        title = location.address

        r = await DL.async_json("http://api.openweathermap.org/data/2.5/forecast?appid={}&lat={}&lon={}".format(
            self.key,
            location.latitude,
            location.longitude
        ))
        days = {}
        for x in r["list"]:
            day = x["dt_txt"].split(" ")[0]
            is_noon = "12:00:00" in x["dt_txt"]
            if not day in days:
                days[day] = {
                    "main": x["main"],
                    "weather": x["weather"],
                    "day_count": 1
                }
                continue
            if x["main"]["temp_min"] < days[day]["main"]["temp_min"]:
                days[day]["main"]["temp_min"] = x["main"]["temp_min"]
            if x["main"]["temp_max"] > days[day]["main"]["temp_max"]:
                days[day]["main"]["temp_max"] = x["main"]["temp_max"]
            days[day]["main"]["temp"] += x["main"]["temp"]
            days[day]["day_count"] += 1
            if is_noon:
                days[day]["weather"] = x["weather"]
        fields = []
        for day in sorted(days):
            days[day]["main"]["temp"] /= days[day]["day_count"]
            fields.append({
                "name": datetime.datetime.strptime(day, "%Y-%m-%d").strftime("%A, %b %d, %Y") + ":",
                "value": self.get_weather_text(days[day], False),
                "inline": True
            })
        await Message.Embed(
            title=title,
            fields=fields,
            color=main_color,
            thumbnail="https://i.ibb.co/CMrsxdX/weather.png"
        ).send(ctx)
        await ctx.message.add_reaction(tick)
