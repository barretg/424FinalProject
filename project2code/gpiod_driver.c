#include <linux/module.h>
#include <linux/of_device.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>
#include <linux/interrupt.h>

unsigned int irq_number;
struct gpio_desc *led_desc, *button_desc;
int led_state = 0;

/**
 * @brief Interrupt service routine is called, when interrupt is triggered
 */
static irq_handler_t gpiod_irq_handler(unsigned int irq, void *dev_id, struct pt_regs *regs) {
	printk("button_gpiod_irq: Interrupt was triggered and ISR was called!\n");
	printk("button_gpiod_irq: This means you pressed the button and now the LED will toggle (I hope)\n");

	led_state = !led_state; // Toggle State
	gpiod_set_value(led_desc, led_state); // Update LED
	
	return (irq_handler_t) IRQ_HANDLED; // Return value denoting that the interrupt has been dealt with. 
}
/**
 * @brief This function is called, when the module is loaded into the kernel
 */
static int setup_button(struct platform_device *pdev) {
	printk("Setting up button \n");

	/* Setup the gpio */
	if((button_desc = devm_gpiod_get(&pdev->dev, "button", GPIOD_IN)) == NULL) {
		printk("Error occurred setting up led! Aborting...\n");
		return -1;
	}
	
	/* Set button debouncing */	
	gpiod_set_debounce(button_desc, 500000);

	/* Setup the interrupt */
	irq_number = gpiod_to_irq(button_desc); 
	if(request_irq(irq_number, (irq_handler_t) gpiod_irq_handler, IRQF_TRIGGER_FALLING, "button_gpiod_irq", NULL) != 0){
		printk("Error!\nCan not request interrupt nr.: %d\n", irq_number);
		// Free the button and LED if it fails
		devm_gpiod_put(&pdev->dev, button_desc);
		devm_gpiod_put(&pdev->dev, led_desc);
		return -1;
	}

	printk("Done!\n");
	printk("GPIO 6 is mapped to IRQ Nr.: %d\n", irq_number);
	return 0;
}

/**
 * @brief This function is called, when the module is removed from the kernel
 */
static void remove_button(struct platform_device *pdev) {
	printk("Removing button\n");
	free_irq(irq_number, NULL); // Free the interrupt
	devm_gpiod_put(&pdev->dev, button_desc); // Free the button
}

/**
 * Checks if there are gpiod pins registered to the functions
 * 'led' and 'button' (in other words, did your overlay work)
 */
static int gpiods_exist(struct platform_device *pdev) {
	int led_c, b_c;
	
	if((led_c = gpiod_count(&pdev->dev, "led")) == -ENOENT) {
		printk("No gpio associated with led!\n");
	}

	if((b_c  = gpiod_count(&pdev->dev, "button")) == -ENOENT) {
		printk("No gpio associated with button!\n");
	}

	if(led_c < 0 || b_c < 0) {
		return 0;
	}
	
	return 1;
}

/**
 * Driver probe function
 */
static int gpiod_probe(struct platform_device *pdev)
{
	printk("Begininng project 2 driver setup...\n");

	// Check if the overlay worked properly 
	if(!gpiods_exist(pdev)) {
		return -1;
	}

	// Get the gpio pin for the button
	led_desc = devm_gpiod_get(&pdev->dev, "led", GPIOD_OUT_LOW);

	// If this fails, abort.
	if(led_desc == NULL) {
		printk("Error occurred setting up led! Aborting...\n");
		return -1;
	}

	// Sync the gpiod value and the led_state variable to avoid gpio value reading
	gpiod_set_value(led_desc, 0);
	led_state = 0;

	printk("LED Settup complete!\n");

	// Set up the button and error handle
	if(setup_button(pdev) < -1) {
		printk("Error setting up button! Freeing led.\n");
		devm_gpiod_put(&pdev->dev, led_desc);
		return -1;
	}

	printk("Button setup complete!\n");
	return 0;
}

/**
 * Driver remove function
 */
static int gpiod_remove(struct platform_device *pdev)
{
	// Free the led and the button
	devm_gpiod_put(&pdev->dev, led_desc);
	remove_button(pdev);

	printk("Removed button and LED!\n");

	return 0;
}




// Driver configuration: 

/**
 * Match table
 */
static struct of_device_id matchy_match[] = {
    { .compatible = "two-compatible"},
    {/* leave alone - keep this here (end node) */},
};

/**
 * Platform driver object
 */
static struct platform_driver gpio_led_driver = {
	.probe	 = gpiod_probe,
	.remove	 = gpiod_remove,
	.driver	 = {
	       .name  = "project-two",
	       .owner = THIS_MODULE,
	       .of_match_table = matchy_match,
	},
};

module_platform_driver(gpio_led_driver);

MODULE_DESCRIPTION("Comp 424 Project 2");
MODULE_AUTHOR("Barret Glass (bmg7)");
MODULE_LICENSE("GPL v2");
MODULE_ALIAS("platform:project-two");
