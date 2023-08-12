library(shiny)
library(ggplot2)
library(data.table)

# Define UI for app that draws a histogram ----
ui <- fluidPage(
  
  # App title ----
  titlePanel("Longevity"),
  
  # Sidebar layout with input and output definitions ----
  sidebarLayout(
    
    # Sidebar panel for inputs ----
    sidebarPanel(
      
      # Input: Slider for the number of bins ----
      sliderInput(inputId = "width",
                  label = "Bandwidth:",
                  min = 50,
                  max = 70,
                  value = 60,
                  step=10)
      
    ),
    
    # Main panel for displaying outputs ----
    mainPanel(
      
      # Vo2 Max and life expectancy
      plotOutput(outputId = "vo2max"),
      plotOutput(outputId = "le")
      
    )
  )
)

# Define server logic required to draw a histogram ----
server <- function(input, output) {
  output$vo2max <- renderPlot({
    ggplot2::ggplot(data=dt[w==input$width,]) +
      geom_line(mapping=aes(x=date, y=vo2max_m), color="blue") +
      geom_point(mapping=aes(x=date, y=vo2max), alpha=0.1) +
      theme_classic() +
      xlab("") + ylab("Vo2 Max (mL/kg/min)")
    
  })
  output$le <- renderPlot({
    ggplot(data=dt[w==input$width,]) +
      geom_line(mapping=aes(x=date, y=le_est_m), color="blue") +
      theme_classic() +
      xlab("") + ylab("Life Expectancy")
    
  })
}

dt = data.table::fread(file="../data/le_estimates.csv")
shinyApp(ui = ui, server = server)
