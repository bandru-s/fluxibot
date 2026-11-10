import asyncio
from dvrip import DVRIPCam #github.com/OpenIPC/python-dvr
from rich import print

#Twitch
bannedusers = ["banned_test"]
channel_name = "#YourChannelName"

#Global control
is_paused = False

#Camera control
is_moving = False
max_x = 10 # max mozgás le-fel (*500ms), megnézni hány mp-ig mozog / 2
max_y = 15 # max mozgás jobbra-balra
x = max_x / 2 # x tengelyen helyzet
y = max_y / 2

#Camera specific
cam_ip = '192.168.1.123'
cam_username = 'admin'
cam_password = 'password'

def setcenterpoint(): #ha a valóságban középre néz a kamera ezzel nullázható a virtuális pozíciója
    global x, y
    x = max_x / 2
    y = max_y / 2

def canmove(dir):
    match dir:
        case "right":
            if y+1 <= max_y:
                return True
            return False
        case "left":
            if y-1 >= 0:
                return True
            return False
        case "up":
            if x+1 <= max_x:
                return True
            return False
        case "down":
            if x-1 >= 0:
                return True
            return False
    

# Setup camera (can remain synchronous at startup)
# cam feed for OBS: rtsp://cam_username:cam_password@cam_ip:554
print("[dim white]INFO: csatlakozás kamerához: [/dim white]"+ cam_ip)
cam = DVRIPCam(cam_ip, user=cam_username, password=cam_password)
cam.login()

print("[bold green] Csatlakozás kamerához sikeres!")

cam.channel_title(["Konfluxus"])
cam.set_time()


# PTZ camera control
def ptz(command, speed=5):
    cam.set_command("OPPTZControl", {
        "Command": command,
        "Parameter": {
            "AUXFunction": {"AUXCode": 0, "Action": 0},
            "Channel": 0,
            "Step": speed,
            "Focus": 0,
            "Iris": 0,
            "PointArg": 0,
            "MenuOpts": "Escape"
        }
    })

def stop():
    ptz("IrisSmall", 0)

# ---- CORE MOVE ----
async def move(direction, duration_ms=500, speed=5):
    global is_moving;
    is_moving = True;
    # Run the blocking camera network calls in a separate thread so they don't block chat
    await asyncio.to_thread(ptz, direction, speed)
    # Non-blocking sleep lets the script read chat while the camera is moving
    await asyncio.sleep(duration_ms / 1000.0)
    await asyncio.to_thread(stop)
    is_moving = False;

# ---- DIRECTIONS ----
async def up(t=500): await move("DirectionUp", t)
async def down(t=500): await move("DirectionDown", t)
async def left(t=500): await move("DirectionLeft", t)
async def right(t=500): await move("DirectionRight", t)
async def up_left(t=500): await move("DirectionLeftUp", t)
async def up_right(t=500): await move("DirectionRightUp", t)
async def down_left(t=500): await move("DirectionLeftDown", t)
async def down_right(t=500): await move("DirectionRightDown", t)
async def zoom_in(t=250): await move("ZoomTile", t)
async def zoom_out(t=250): await move("ZoomWide", t)
 # Available directions:
        #    "DirectionUp",
        #     "DirectionDown",
        #     "DirectionLeft",
        #     "DirectionRight",
        #     "DirectionLeftUp",
        #     "DirectionLeftDown",
        #     "DirectionRightUp",
        #     "DirectionRightDown",
        #    "ZoomTile",
        #     "ZoomWide",
        #     "FocusNear",
        #     "FocusFar",
        #     "IrisSmall",
        #     "IrisLarge",
        #     "SetPreset",
        #     "GotoPreset",
        #     "ClearPreset",
        #     "StartTour",
        #     "StopTour", 

# ENTER command
async def terminal_listener():
    global is_paused, bannedusers
    while True:
        cmd = await asyncio.to_thread(input)
        cmd = cmd.strip().lower()
        if cmd == "h":
            print("🤖 [bold purple]FluxiBot [/bold purple] parancsok listája:")
            print("[bold white]pause:[/bold white] [dim white]ne figyelje a parancsokat (nem mozog a kamera)[/dim white]")
            print("[bold white]start:[/bold white] [dim white]figyelje megint a parancsokat (nem mozog a kamera)[/dim white]")
            print("[bold white]ban (név):[/bold white] [dim white]letiltja (név) usert[/dim white]")
            print("[bold white]center :[/bold white] [dim white]kamera középre néző állása[/dim white]")
        elif cmd == "pause":
            is_paused = True
            print("[bold yellow]SYSTEM: Bot PAUSED. Nem teljesíti a parancsokat.[/bold yellow]")
        
        elif cmd == "center" or cmd =="reset":
            setcenterpoint()
            print("[bold green]SYSTEM: Kamera középpont beállítva[/bold green]")

        elif cmd == "start":
            is_paused = False
            print("[bold green]SYSTEM: Bot MEGYEN. Figyeli a csetet...[/bold green]")
        
        elif cmd.startswith("ban "):
            # Extract the username after the word "ban "
            user_to_ban = cmd.split(" ", 1)[1].strip()
            if user_to_ban not in bannedusers:
                bannedusers.append(user_to_ban)
                print(f"[bold red]SYSTEM: User '{user_to_ban}' BAN.[/bold red]")
            else:
                print(f"[yellow]SYSTEM: User '{user_to_ban}' már BAN.[/yellow]")
        
        elif cmd:
            print("[dim white]SYSTEM: Ismeretlen parancs, írd be 'h'[/dim white]")


#beolvasott chat üzenetek mit csináljanak
#Parse commands from chat messages
async def checkcommand(txt):
    global x,y
    match txt:
        case "right":
            if canmove("right"):
                y += 1
                await right()
        case "left":
            if canmove("left"):
                y -= 1
                await left()
        case "up":
            if canmove("up"):
                x += 1
                await up()
        case "down":
            if canmove("down"):
                x -= 1
                await down()
        case "zin":
                await zoom_in()
        case "zout":
            await zoom_out()
        case _:
            return

async def main():
    # Twitch IRC server details
    global channel_name
    SERVER = "irc.chat.twitch.tv"
    PORT = 6667
    NICK = "justinfan12345"  # anonymous nickname
    CHANNEL = channel_name

    print("🤖 [bold purple]FluxiBot [/bold purple][bold green]elindult!")

    # Start the terminal listener in the background
    asyncio.create_task(terminal_listener())
    print("[cyan]Admin Konzol fut![/cyan] parancsok listájához írd be, hogy 'h' és nyomj Entert.")
    print(f"[dim white]Kapcsolódás csatornához:[/dim white] {CHANNEL}")
    # Create async socket connection
    reader, writer = await asyncio.open_connection(SERVER, PORT)

    # Send anonymous login
    writer.write(f"NICK {NICK}\r\n".encode("utf-8"))
    writer.write(f"JOIN {CHANNEL}\r\n".encode("utf-8"))
    await writer.drain()

    print(f"[green]Kapcsolódva {CHANNEL}! Mutatom az üzeneteket:")

    while True:
        # Read line by line asynchronously
        line = await reader.readline()
        if not line:
            break  # Connection closed
        
        resp = line.decode("utf-8").strip()

        if resp.startswith("PING"):
            writer.write("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            await writer.drain()
        else:
            try:
                if "PRIVMSG" in resp:
                    prefix, msg = resp.split("PRIVMSG", 1)
                    user = prefix.split("!")[0][1:]
                    text = msg.split(" :", 1)[1]
                    
                    if user not in bannedusers:
                        print(f"[bold purple]{user}:[/bold purple] [bold white]{text}")
                        
                        # create_task schedules the camera move in the background 
                        # so the while loop immediately continues listening to chat
                        if not is_paused and not is_moving:
                            asyncio.create_task(checkcommand(text))
                else:
                    print(f"[dim white]INFO: Not PRIVMSG: [/dim white][white] {resp}")
            except:
                print(f"[bold red]ERROR: can't parse message: [/bold red][bold white] {resp}")

if __name__ == "__main__":
    # Start the asyncio event loop
    asyncio.run(main())