-- This script shows how to fly to different points in Positioning system

-- Simplification and caching table.unpack calls
local unpack = table.unpack

-- Base pcb number of RGB LEDs
local ledNumber = 4
-- RGB LED control port initialize
local leds = Ledbar.new(ledNumber)

-- Function changes color on all LEDs
local function changeColor(color)
    -- Changing color on each LED one after another
    for i=0, ledNumber - 1, 1 do
        leds:set(i, unpack(color))
    end
end

-- Table of colors in RGB form for changeColor function
local colors = {
        {1, 1, 0}, -- yellow
        {1, 0, 1}, -- violet
        {0, 1, 1}, -- cyan
        {1, 1, 1}, -- white
}

-- Current point variable
-- changeColor(colors[1])

-- Event processing function called automatically by autopilot
function callback(event)

end

-- changeColor(colors[7])

function connect()
    mailbox.connect("192.168.4.2", 8889)
end

function echo()
    local hull = -1
    local message = ""
    for i=1,2 do
        hull, message = mailbox.receive(true)
        mailbox.send(hull, message)
    end
    mailbox.send(hull, "Man, I'm tired. Leave me alone")
end

function echochk()
    local hull = -1
    local message = ""
    local ncolors = 4
    local icolor = 1

    changeColor({1, 1, 1})
    while (icolor ~= ncolors + 1) do
        if mailbox.hasMessages() then
            hull, message = mailbox.receive(false)
            mailbox.send(hull, message)
            changeColor(colors[icolor])
            icolor = icolor + 1
        end
    end
    mailbox.send(hull, "Oops. I'm out of colors...")
    changeColor({0, 0, 0})
end

function send()
    mailbox.send(888, "Hi. Let's get to know each other. Here is my hull number. Call me")
    mailbox.send(888, tostring(mailbox.myHullNumber()))
end

function sendall()
    mailbox.send(-1, "Hi everyone")
end

function sendHullNumber()
    mailbox.setHullNumber(11)
    send()
end

-- send()
-- sendall()
connect()
sendHullNumber()
-- echo()
-- echochk()
changeColor(colors[5])




