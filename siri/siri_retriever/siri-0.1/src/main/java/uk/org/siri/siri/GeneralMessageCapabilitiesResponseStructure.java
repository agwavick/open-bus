//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, vJAXB 2.1.10 in JDK 6 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2010.11.14 at 03:28:36 PM PST 
//


package uk.org.siri.siri;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlType;
import javax.xml.bind.annotation.adapters.CollapsedStringAdapter;
import javax.xml.bind.annotation.adapters.XmlJavaTypeAdapter;


/**
 * Data type for Delivery for General MessageService
 * 
 * <p>Java class for GeneralMessageCapabilitiesResponseStructure complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="GeneralMessageCapabilitiesResponseStructure">
 *   &lt;complexContent>
 *     &lt;extension base="{http://www.siri.org.uk/siri}AbstractServiceCapabilitiesResponseStructure">
 *       &lt;sequence>
 *         &lt;element ref="{http://www.siri.org.uk/siri}GeneralMessageServiceCapabilities" minOccurs="0"/>
 *         &lt;element ref="{http://www.siri.org.uk/siri}GeneralMessagePermissions" minOccurs="0"/>
 *         &lt;element ref="{http://www.siri.org.uk/siri}Extensions" minOccurs="0"/>
 *       &lt;/sequence>
 *       &lt;attribute name="version" use="required" type="{http://www.siri.org.uk/siri}VersionString" fixed="1.3" />
 *     &lt;/extension>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "GeneralMessageCapabilitiesResponseStructure", propOrder = {
    "generalMessageServiceCapabilities",
    "generalMessagePermissions",
    "extensions"
})
public class GeneralMessageCapabilitiesResponseStructure
    extends AbstractServiceCapabilitiesResponseStructure
{

    @XmlElement(name = "GeneralMessageServiceCapabilities")
    protected GeneralMessageServiceCapabilitiesStructure generalMessageServiceCapabilities;
    @XmlElement(name = "GeneralMessagePermissions")
    protected GeneralMessagePermissions generalMessagePermissions;
    @XmlElement(name = "Extensions")
    protected ExtensionsStructure extensions;
    @XmlAttribute(required = true)
    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    protected String version;

    /**
     * Gets the value of the generalMessageServiceCapabilities property.
     * 
     * @return
     *     possible object is
     *     {@link GeneralMessageServiceCapabilitiesStructure }
     *     
     */
    public GeneralMessageServiceCapabilitiesStructure getGeneralMessageServiceCapabilities() {
        return generalMessageServiceCapabilities;
    }

    /**
     * Sets the value of the generalMessageServiceCapabilities property.
     * 
     * @param value
     *     allowed object is
     *     {@link GeneralMessageServiceCapabilitiesStructure }
     *     
     */
    public void setGeneralMessageServiceCapabilities(GeneralMessageServiceCapabilitiesStructure value) {
        this.generalMessageServiceCapabilities = value;
    }

    /**
     * Gets the value of the generalMessagePermissions property.
     * 
     * @return
     *     possible object is
     *     {@link GeneralMessagePermissions }
     *     
     */
    public GeneralMessagePermissions getGeneralMessagePermissions() {
        return generalMessagePermissions;
    }

    /**
     * Sets the value of the generalMessagePermissions property.
     * 
     * @param value
     *     allowed object is
     *     {@link GeneralMessagePermissions }
     *     
     */
    public void setGeneralMessagePermissions(GeneralMessagePermissions value) {
        this.generalMessagePermissions = value;
    }

    /**
     * Gets the value of the extensions property.
     * 
     * @return
     *     possible object is
     *     {@link ExtensionsStructure }
     *     
     */
    public ExtensionsStructure getExtensions() {
        return extensions;
    }

    /**
     * Sets the value of the extensions property.
     * 
     * @param value
     *     allowed object is
     *     {@link ExtensionsStructure }
     *     
     */
    public void setExtensions(ExtensionsStructure value) {
        this.extensions = value;
    }

    /**
     * Gets the value of the version property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getVersion() {
        if (version == null) {
            return "1.3";
        } else {
            return version;
        }
    }

    /**
     * Sets the value of the version property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setVersion(String value) {
        this.version = value;
    }

}
