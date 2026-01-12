"""
Pydantic models for Valuation Report schema.
Maps to the Mongoose schema in valuation Report Schema.txt
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class PropertyType(BaseModel):
    """Property type classification and tenure details"""
    isDetachedHouse: Optional[bool] = None
    isSemiDetachedHouse: Optional[bool] = None
    isTerracedHouse: Optional[bool] = None
    isBungalow: Optional[bool] = None
    isFlat: Optional[bool] = None
    isMaisonette: Optional[bool] = None
    flatMaisonetteFloor: Optional[int] = None
    numberOfFloorsInBlock: Optional[int] = None
    isBuiltOrOwnedByLocalAuthority: Optional[bool] = None
    ownerOccupationPercentage: Optional[float] = None
    isFlatMaisonetteConverted: Optional[bool] = None
    conversionYear: Optional[int] = None
    isPurposeBuilt: Optional[bool] = None
    numberOfUnitsInBlock: Optional[int] = None
    isAboveCommercial: Optional[bool] = None
    residentialNatureImpact: Optional[str] = None
    tenure: Optional[str] = None
    isFlyingFreehold: Optional[bool] = None
    flyingFreeholdPercentage: Optional[float] = None
    maintenanceCharge: Optional[float] = None
    roadCharges: Optional[float] = None
    groundRent: Optional[float] = None
    remainingLeaseTermYears: Optional[int] = None
    isPartCommercialUse: Optional[bool] = None
    commercialUsePercentage: Optional[float] = None
    isPurchasedUnderSharedOwnership: Optional[bool] = None
    yearBuilt: Optional[int] = None


class Accommodation(BaseModel):
    """Room counts and dwelling details"""
    hall: Optional[int] = None
    livingRooms: Optional[int] = None
    kitchen: Optional[int] = None
    isLiftPresent: Optional[bool] = None
    utility: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    separateWc: Optional[int] = None
    basement: Optional[int] = None
    garage: Optional[int] = None
    parking: Optional[int] = None
    gardens: Optional[bool] = None
    isPrivate: Optional[bool] = None
    isCommunal: Optional[bool] = None
    numberOfOutbuildings: Optional[int] = None
    outbuildingDetails: Optional[str] = None
    grossFloorAreaOfDwelling: Optional[float] = None


class CurrentOccupancy(BaseModel):
    """Current occupancy status"""
    isEverOccupied: Optional[bool] = None
    numberOfAdultsInProperty: Optional[int] = None
    isHmoOrMultiUnitFreeholdBlock: Optional[bool] = None
    isCurrentlyTenanted: Optional[bool] = None
    hmoOrMultiUnitDetails: Optional[str] = None


class NewBuild(BaseModel):
    """New build / recently converted property details"""
    isNewBuildOrRecentlyConverted: Optional[bool] = None
    isCompleted: Optional[bool] = None
    isUnderConstruction: Optional[bool] = None
    isFinalInspectionRequired: Optional[bool] = None
    isNhbcCert: Optional[bool] = None
    isBuildZone: Optional[bool] = None
    isPremier: Optional[bool] = None
    isProfessionalConsultant: Optional[bool] = None
    isOtherCert: Optional[bool] = None
    otherCertDetails: Optional[str] = None
    isSelfBuildProject: Optional[bool] = None
    isInvolvesPartExchange: Optional[bool] = None
    isDisclosureOfIncentivesSeen: Optional[bool] = None
    incentivesDetails: Optional[str] = None
    newBuildDeveloperName: Optional[str] = None


class Construction(BaseModel):
    """Construction materials and alterations"""
    isStandardConstruction: Optional[bool] = None
    nonStandardConstructionType: Optional[str] = None
    mainWalls: Optional[str] = None
    mainRoof: Optional[str] = None
    garageConstruction: Optional[str] = None
    outbuildingsConstruction: Optional[str] = None
    isHasAlterationsOrExtensions: Optional[bool] = None
    isAlterationsRequireConsents: Optional[bool] = None
    alterationsAge: Optional[int] = None


class LocalityAndDemand(BaseModel):
    """Location type, market conditions, and local factors"""
    isUrban: Optional[bool] = None
    isSuburban: Optional[bool] = None
    isRural: Optional[bool] = None
    isGoodMarketAppeal: Optional[bool] = None
    isAverageMarketAppeal: Optional[bool] = None
    isPoorMarketAppeal: Optional[bool] = None
    isOwnerResidential: Optional[bool] = None
    isResidentialLet: Optional[bool] = None
    isCommercial: Optional[bool] = None
    isPricesRising: Optional[bool] = None
    isPricesStatic: Optional[bool] = None
    isPricesFalling: Optional[bool] = None
    isDemandRising: Optional[bool] = None
    isDemandStatic: Optional[bool] = None
    isDemandFalling: Optional[bool] = None
    isAffectedByCompulsoryPurchase: Optional[bool] = None
    compulsoryPurchaseDetails: Optional[str] = None
    isVacantOrBoardedPropertiesNearby: Optional[bool] = None
    vacantOrBoardedDetails: Optional[str] = None
    isOccupancyRestrictionPossible: Optional[bool] = None
    occupancyRestrictionDetails: Optional[str] = None
    isCloseToHighVoltageEquipment: Optional[bool] = None
    highVoltageEquipmentDetails: Optional[str] = None


class Services(BaseModel):
    """Utilities and access details"""
    isMainsWater: Optional[bool] = None
    isPrivateWater: Optional[bool] = None
    isUnknownWater: Optional[bool] = None
    isGasSupply: Optional[bool] = None
    isElectricitySupply: Optional[bool] = None
    isCentralHeating: Optional[bool] = None
    centralHeatingType: Optional[str] = None
    isMainDrainage: Optional[bool] = None
    isSepticTankPlant: Optional[bool] = None
    isUnknownDrainage: Optional[bool] = None
    isSolarPanels: Optional[bool] = None
    isSharedAccess: Optional[bool] = None
    isRoadAdopted: Optional[bool] = None
    isHasEasementsOrRightsOfWay: Optional[bool] = None
    easementsOrRightsDetails: Optional[str] = None
    servicesSeparateForFlats: Optional[str] = None
    servicesSeparateDetails: Optional[str] = None


class PropertyProneTo(BaseModel):
    """Environmental hazard risks"""
    flooding: Optional[bool] = None
    subsidence: Optional[bool] = None
    heave: Optional[bool] = None
    landslip: Optional[bool] = None
    details: Optional[str] = None


class ConditionsOfProperty(BaseModel):
    """Structural condition and site factors"""
    isStructuralMovement: Optional[bool] = None
    isStructuralMovementHistoricOrNonProgressive: Optional[bool] = None
    structuralMovementDetails: Optional[str] = None
    isStructuralModifications: Optional[bool] = None
    structuralModificationsDetails: Optional[str] = None
    communalAreasMaintained: Optional[bool] = None
    propertyProneTo: Optional[PropertyProneTo] = None
    isPlotBoundariesDefinedUnderPointFourHectares: Optional[bool] = None
    isTreesWithinInfluencingDistance: Optional[bool] = None
    treesInfluenceDetails: Optional[str] = None
    isBuiltOnSteepSlope: Optional[bool] = None
    steepSlopeDetails: Optional[str] = None


class Reports(BaseModel):
    """Specialist reports required"""
    isTimberDamp: Optional[bool] = None
    isMining: Optional[bool] = None
    isElectrical: Optional[bool] = None
    isDrains: Optional[bool] = None
    isStructuralEngineers: Optional[bool] = None
    isArboricultural: Optional[bool] = None
    isMundic: Optional[bool] = None
    isWallTies: Optional[bool] = None
    isRoof: Optional[bool] = None
    isMetalliferous: Optional[bool] = None
    isSulfateRedAsh: Optional[bool] = None
    isOtherReport: Optional[bool] = None
    otherReportDetails: Optional[str] = None


class EnergyEfficiency(BaseModel):
    """EPC rating details"""
    epcRating: Optional[str] = None
    epcScore: Optional[int] = None


class EssentialRepairs(BaseModel):
    """Required repairs information"""
    isEssentialRepairsRequired: Optional[bool] = None
    essentialRepairsDetails: Optional[str] = None
    isReinspectionRequired: Optional[bool] = None


class RentalInformation(BaseModel):
    """Rental market details"""
    isRentalDemandInLocality: Optional[bool] = None
    rentalDemandDetails: Optional[str] = None
    monthlyMarketRentPresentCondition: Optional[float] = None
    monthlyMarketRentImprovedCondition: Optional[float] = None
    isOtherLettingDemandFactors: Optional[bool] = None
    otherLettingDemandDetails: Optional[str] = None
    investorOnlyDemand: Optional[bool] = None
    investorOnlyDemandDetails: Optional[str] = None


class ValuationForFinancePurpose(BaseModel):
    """Market valuation details"""
    valuationComparativeOnly: Optional[str] = None
    isSuitableForFinance: Optional[bool] = None
    financeSuitabilityDetails: Optional[str] = None
    marketValuePresentCondition: Optional[float] = None
    marketValueAfterRepairs: Optional[float] = None
    purchasePriceOrBorrowerEstimate: Optional[float] = None
    buildingInsuranceReinstatementCost: Optional[float] = None
    isInsurancePremiumLoadingRisk: Optional[bool] = None
    insurancePremiumLoadingDetails: Optional[str] = None


class ValuerQualifications(BaseModel):
    """Valuer professional qualifications"""
    mrics: Optional[bool] = None
    frics: Optional[bool] = None
    assocRics: Optional[bool] = None


class ValuersDeclaration(BaseModel):
    """Valuer's signature and contact details"""
    valuerSignature: Optional[str] = None
    valuerName: Optional[str] = None
    onBehalfOf: Optional[str] = None
    telephone: Optional[str] = None  # Keep as string to preserve formatting
    fax: Optional[str] = None
    email: Optional[str] = None
    valuerQualifications: Optional[ValuerQualifications] = None
    ricsNumber: Optional[int] = None
    valuerAddress: Optional[str] = None
    valuerPostcode: Optional[str] = None
    reportDate: Optional[str] = None  # ISO date string


class ValuationReport(BaseModel):
    """
    Main Valuation Report model.
    Maps to ApplicationValuationReport in Mongoose schema.
    """
    # Header fields
    applicationType: Optional[str] = None
    applicationNumber: Optional[str] = None
    applicantName: Optional[str] = None
    dateOfInspection: Optional[str] = None  # ISO date string
    propertyAddress: Optional[str] = None
    postCode: Optional[str] = None
    
    # Nested sections
    propertyType: Optional[PropertyType] = None
    accommodation: Optional[Accommodation] = None
    currentOccupency: Optional[CurrentOccupancy] = None  # Note: typo preserved from schema
    newBuild: Optional[NewBuild] = None
    construction: Optional[Construction] = None
    localityAndDemand: Optional[LocalityAndDemand] = None
    services: Optional[Services] = None
    conditionsOfProperty: Optional[ConditionsOfProperty] = None
    reports: Optional[Reports] = None
    energyEfficiency: Optional[EnergyEfficiency] = None
    essentialRepairs: Optional[EssentialRepairs] = None
    rentalInformation: Optional[RentalInformation] = None
    valuationForFinancePurpose: Optional[ValuationForFinancePurpose] = None
    valuationForFinancePurposeHPP: Optional[ValuationForFinancePurpose] = None
    generalRemarks: Optional[str] = None
    valuersDeclaration: Optional[ValuersDeclaration] = None
    
    # Metadata (not extracted from PDF)
    extractedText: Optional[str] = None
