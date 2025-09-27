package main

import (
	"encoding/json"
	"fmt"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/rivo/tview"
)

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
	return func(Client mqtt.Client, err error) {
		fmt.Fprintf(textView, "") // Empty string so connection messages do not fill application
	}
}

var connectLostHandler = func(textView *tview.TextView) mqtt.connectLostHandler {
	return func(Client mqtt.Client, err error) {
		fmt.Fprintf(textView, "Connection lost: %v\n", err)
	}
}

func mqtt_messagePubHandler(app *tview.Application, textView *tview.TextView) mqtt.MessageHandler {
	return func(Client mqtt.Client, msg mqtt.Message) {
		var s SystemData

		if err := json.Unmarshal(msg.Payload(), &d); err != nil {
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
	newPrimitive := func(text string) tview.Primitive {
		return tview.NewTextView().
			SetTextAlign(tview.AlignCenter).
			SetText(text)
	}
	menu := newPrimitive("Menu")
	main := newPrimitive("Main content")
	sideBar := newPrimitive("Side Bar")

	grid := tview.NewGrid().
		SetRows(3, 0, 3).
		SetColumns(30, 0, 30).
		SetBorders(true).
		AddItem(newPrimitive("Header"), 0, 0, 1, 3, 0, 0, false).
		AddItem(newPrimitive("Footer"), 2, 0, 1, 3, 0, 0, false)

	// Layout for screens narrower than 100 cells (menu and side bar are hidden).
	grid.AddItem(menu, 0, 0, 0, 0, 0, 0, false).
		AddItem(main, 1, 0, 1, 3, 0, 0, false).
		AddItem(sideBar, 0, 0, 0, 0, 0, 0, false)

	// Layout for screens wider than 100 cells.
	grid.AddItem(menu, 1, 0, 1, 1, 0, 100, false).
		AddItem(main, 1, 1, 1, 1, 0, 100, false).
		AddItem(sideBar, 1, 2, 1, 1, 0, 100, false)

	if err := tview.NewApplication().SetRoot(grid, true).EnableMouse(true).Run(); err != nil {
		panic(err)
	}
}
