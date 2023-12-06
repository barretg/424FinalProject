#include <linux/module.h>
#include <linux/of_device.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>
#include <linux/interrupt.h>

unsigned int irq_number;
struct gpio_desc *encoder_desc;
int speed = 0;

/**
 * @brief Interrupt service routine is called, when interrupt is triggered
 */
static irq_handler_t gpiod_irq_handler(unsigned int irq, void *dev_id, struct pt_regs *regs) {
	printk("encoder_gpiod_irq: Interrupt was triggered and ISR was called!\n");
	printk("encoder_gpiod_irq: This means that the encoder triggered\n");


  //TODO: make this measure speed and store that output in a file.
  

	return (irq_handler_t) IRQ_HANDLED; // Return value denoting that the interrupt has been dealt with. 
}
/**
 * @brief This function is called, when the module is loaded into the kernel
 */
static int setup_encoder(struct platform_device *pdev) {
	printk("Setting up encoder\n");

	/* Setup the gpio */
	if((encoder_desc = devm_gpiod_get(&pdev->dev, "encoder", GPIOD_IN)) == NULL) {
		printk("Error occurred setting up encoder! Aborting...\n");
		return -1;
	}
	
	//gpiod_set_debounce(encoder_desc 5000);

	/* Setup the interrupt */
	irq_number = gpiod_to_irq(encoder_desc); 
	if(request_irq(irq_number, (irq_handler_t) gpiod_irq_handler, IRQF_TRIGGER_FALLING, "encoder_gpiod_irq", NULL) != 0){
		printk("Error!\nCan not request interrupt nr.: %d\n", irq_number);
		// Free the encoder if it fails
		devm_gpiod_put(&pdev->dev, encoder_desc);
		return -1;
	}

	printk("Done!\n");
	printk("GPIO 24 is mapped to IRQ Nr.: %d\n", irq_number);
	return 0;
}

/**
 * @brief This function is called, when the module is removed from the kernel
 */
static void remove_encoder(struct platform_device *pdev) {
	printk("Removing encoder\n");
	free_irq(irq_number, NULL); // Free the interrupt
	devm_gpiod_put(&pdev->dev, encoder_desc); // Free the encoder
}

/**
 * Checks if there are gpiod pins registered to the functions
 * 'encoder' (in other words, did your overlay work)
 */
static int gpiods_exist(struct platform_device *pdev) {
	int b_c;
	
	if((b_c  = gpiod_count(&pdev->dev, "encoder")) == -ENOENT) {
		printk("No gpio associated with encoder!\n");
	}

	if(b_c < 0) {
		return 0;
	}
	
	return 1;
}

/**
 * Driver probe function
 */
static int gpiod_probe(struct platform_device *pdev)
{
	printk("Begininng speed encoder driver setup...\n");

	// Check if the overlay worked properly 
	if(!gpiods_exist(pdev)) {
		return -1;
	}

	// Set up the encoder and error handle
	if(setup_encoder(pdev) < -1) {
		printk("Error setting up encoder!\n");
		return -1;
	}

	printk("Encoder setup complete!\n");
	return 0;
}

/**
 * Driver remove function
 */
static int gpiod_remove(struct platform_device *pdev)
{
	// Free the encoder
	remove_encoder(pdev);

	printk("Removed encoder!\n");

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
static struct platform_driver gpio_encoder_driver = {
	.probe	 = gpiod_probe,
	.remove	 = gpiod_remove,
	.driver	 = {
	       .name  = "final-project",
	       .owner = THIS_MODULE,
	       .of_match_table = matchy_match,
	},
};

module_platform_driver(gpio_encoder_driver);

MODULE_DESCRIPTION("Comp 424 Project 2");
MODULE_AUTHOR("Barret Glass (bmg7)");
MODULE_LICENSE("GPL v2");
MODULE_ALIAS("platform:project-two");
