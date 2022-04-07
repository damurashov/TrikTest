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
    mailbox.connect(192, 168, 4, 2, 8889)
end

function echo()
    local hull = -1
    local message = ""
    for i=1,2 do
        message, hull = mailbox.receive(true)
        mailbox.send(message, hull)
    end
    mailbox.send("Man, I'm tired. Leave me alone", hull)
end

function echochk()
    local hull = -1
    local message = ""
    local ncolors = 4
    local icolor = 1

    changeColor({1, 1, 1})
    while (icolor ~= ncolors + 1) do
        if mailbox.hasMessages() then
            message, hull = mailbox.receive(false)
            mailbox.send(message, hull)
            changeColor(colors[icolor])
            icolor = icolor + 1
        end
    end
    mailbox.send("Oops. I'm out of colors...", hull)
    changeColor({0, 0, 0})
end

function send()
    mailbox.send("Hi", 888)
end

function sendall()
    mailbox.send("Hi everyone", -1)
end

-- send()
-- sendall()
-- connect()
-- echo()
echochk()

-- -- Timer creation, that calls our function each 0.1 second
-- t = Timer.new(1, function() connect() end)
-- -- Timer start
-- t:start()

changeColor(colors[5])

-- Changing LEDs color to white




