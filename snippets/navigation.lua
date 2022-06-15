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

function loopNavCommand()
    local hull = -1
    local message = ""

    changeColor(colors[4])

    while (1) do
        hull, message = mailbox.receive(true)

        if (hull > 0) then
            mailbox.send(hull, "Acknowledged")

            if message == "arm" then
                ap.push(Ev.MCE_PREFLIGHT)
            elseif message == "takeoff" then
                ap.push(Ev.MCE_TAKEOFF)
            elseif message == "forward" then
                ap.goToLocalPoint({1, 0, .7})
            elseif message == "land" then
                ap.push(Ev.MCE_LANDING)
            elseif message == "done" then
                break
            end
        end
    end

    changeColor({0, 0, 0})
end

loopNavCommand()
