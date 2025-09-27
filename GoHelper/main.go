package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
	"gopkg.in/yaml.v3"
)

// Struct for hosts file
type Config struct {
	Hosts []Host `yaml:"hosts"`
}

type Host struct {
	Name string `yaml:"name"`
	IP   string `yaml:"ip`
}

// Structs to handle MQTT Data
type SystemData struct {
	Hostname       string              `json:"Hostname"`
	OSVersion      string              `json:"OS Version"`
	Kernel         string              `json:"Kernel"`
	Uptime         string              `json:"Uptime"`
	TotalRAM       string              `json:"Total RAM"`
	CPUInfo        CPUInfo             `json:"CPU Info"`
	SwapInfo       SwapInfo            `json:"Swap Info"`
	DiskInfo       map[string]DiskInfo `json:"Disk Info"` // disks are dynamic keys
	NetworkInfo    NetworkInfo         `json:"Network Info"`
	Virtualization string              `json:"Virtualization"`
}

type CPUInfo struct {
	ModelName string `json:"model name"`
	VendorID  string `json:"vendor_id"`
	Cores     string `json:"cpu cores"`
	CacheSize string `json:"cache size"`
	CPUMHz    string `json:"cpu MHz"`
}

type SwapInfo struct {
	Total     string `json:"Total Swap"`
	Used      string `json:"Used Swap"`
	Available string `json:"Avaiable Swap"`
}

type DiskInfo struct {
	TotalSize      string `json:"Total Size"`
	UsedSpace      string `json:"Used Space"`
	AvailableSpace string `json:"Avaiable Space"`
	PercentUse     string `json:"Percentage Use"`
	MountPoint     string `json:"Mount Point"`
}

type NetworkInfo struct {
	IPv4 string `json:"IPV4 Address"`
	MAC  string `json:"MAC Address"`
}

// ===== BEGIN MQTT FUNCTIONS =====
var connectHandler = func(textView *tview.TextView) mqtt.OnConnectHandler {
	return func(Client mqtt.Client) {
		fmt.Fprintf(textView, "") // Empty string so connection messages do not fill application
	}
}

var connectLostHandler = func(textView *tview.TextView) mqtt.ConnectionLostHandler {
	return func(Client mqtt.Client, err error) {
		fmt.Fprintf(textView, "Connection lost: %v\n", err)
	}
}

func mqtt_messagePubHandler(app *tview.Application, textView *tview.TextView) mqtt.MessageHandler {
	return func(Client mqtt.Client, msg mqtt.Message) {
		var s SystemData

		if err := json.Unmarshal(msg.Payload(), &s); err != nil {
			fmt.Fprintf(textView, "JSON Decode Error: %v\n", err)
		}

		app.QueueUpdateDraw(func() {
			textView.Clear()

			fmt.Fprintf(textView, " ===================\n Basic Information\n ")
			fmt.Fprintf(textView, "   Hostname: %s\n", s.Hostname)
			fmt.Fprintf(textView, "   OS Version: %s\n", s.OSVersion)
			fmt.Fprintf(textView, "   Virtualization: %s\n", s.Virtualization)
			fmt.Fprintf(textView, "   Kernel: %s\n", s.Kernel)
			fmt.Fprintf(textView, "   Uptime: %s\n", s.Uptime)
			fmt.Fprintf(textView, " ===================\n CPU Information\n ")
			fmt.Fprintf(textView, "   Model Name: %s\n", s.CPUInfo.ModelName)
			fmt.Fprintf(textView, "   Cores: %s\n", s.CPUInfo.Cores)
			fmt.Fprintf(textView, "   Refresh Rate: %sMHz\n", s.CPUInfo.CPUMHz)
			fmt.Fprintf(textView, " ===================\n Network Information\n ")
			fmt.Fprintf(textView, "   IPv4 Address: %s\n", s.NetworkInfo.IPv4)
			fmt.Fprintf(textView, "   MAC Address: %s\n", s.NetworkInfo.MAC)
		})
	}
}

func sub_MQTT(Client mqtt.Client, app *tview.Application, textView *tview.TextView) {
	topic := "system/+"
	token := Client.Subscribe(topic, 1, mqtt_messagePubHandler(app, textView))
	token.Wait()
}

func main() {
	// Read the yaml file
	data, err := os.ReadFile("hosts.yml")
	if err != nil {
		log.Fatalf("Error reading yaml file: %v", err)
	}

	// Parse into Config
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		log.Fatalf("Error processing data: %v", err)
	}

	app := tview.NewApplication()
	pages := tview.NewPages()

	// Main list for hosts
	list := tview.NewList()
	pages.AddPage("list", list, true, true)

	// Loop through hosts and add to application
	for i, host := range cfg.Hosts {
		h := host

		itemText := fmt.Sprintf("%s (%s)", h.Name, h.IP)
		list.AddItem(strings.ToUpper(itemText), "Press Enter to Select Host", rune('1'+i), func() {
			// Create header and footer for grid
			var header *tview.TextView
			header = tview.NewTextView()
			header.SetBorder(true)
			header.SetText(fmt.Sprintf("HOST: %s", strings.ToUpper(h.Name)))
			header.SetTextAlign(tview.AlignCenter)

			var footer *tview.TextView
			footer = tview.NewTextView()
			footer.SetBorder(true)
			footer.SetText("Data will refresh at regular intervals - 'q' to quit")
			footer.SetTextAlign(tview.AlignCenter)

			// Create the grid
			grid := tview.NewGrid().
				SetRows(3, 0, 3).
				SetColumns(30, 0, 30).
				SetBorders(true).
				AddItem(header, 0, 0, 1, 3, 0, 0, false).
				AddItem(footer, 2, 0, 1, 3, 0, 0, false)

			// Create textView's for data
			var textView_MQTT *tview.TextView
			textView_MQTT = tview.NewTextView()
			textView_MQTT.SetDynamicColors(true).
				SetTitle(" MQTT Data ").
				SetTitleAlign(tview.AlignCenter)

			// Add items to the grid
			grid.AddItem(textView_MQTT, 1, 0, 1, 1, 0, 0, true)
			grid.AddItem(textView_MQTT, 1, 2, 1, 1, 0, 0, true)
			grid.AddItem(textView_MQTT, 1, 1, 1, 1, 0, 0, true)

			// Set pages: list <-> grid
			pages.AddAndSwitchToPage("grid", grid, true)

			go func() {
				var broker = h.IP
				var port = 1883

				// Set options for MQTT
				opts := mqtt.NewClientOptions()
				opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, port))
				opts.SetClientID("MQTT")
				opts.OnConnect = connectHandler(textView_MQTT)
				opts.OnConnectionLost = connectLostHandler(textView_MQTT)
				MQTT_Output := mqtt.NewClient(opts)

				if token := MQTT_Output.Connect(); token.Wait() && token.Error() != nil {
					panic(token.Error())
				}

				sub_MQTT(MQTT_Output, app, textView_MQTT)

				grid.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
					if event.Key() == tcell.KeyEsc || event.Rune() == 'q' {
						MQTT_Output.Disconnect(250)
						pages.SwitchToPage("list")
						return nil
					}
					return event
				})
			}()
		})
	}

	list.AddItem("Quit", "Press to exit", 'q', func() {
		app.Stop()
	})

	if err := app.SetRoot(pages, true).EnableMouse(true).Run(); err != nil {
		panic(err)
	}
}
